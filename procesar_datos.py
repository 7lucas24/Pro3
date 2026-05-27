import os
import ray
import pyarrow as pa
import pandas as pd
import time

def process_csv_to_parquet():
    print("Inicializando Ray...")
    ray.init(ignore_reinit_error=True)
    
    input_dir = "accidentes/conjunto_de_datos"
    output_dir = "accidentes_parquet"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Leyendo CSVs desde {input_dir}...")
    start_time = time.time()
    
    # Custom read with pandas in a Ray task to handle messy CSVs
    @ray.remote
    def process_file(filename):
        filepath = os.path.join(input_dir, filename)
        try:
            # Read CSV. It has weird whitespaces and possibly a BOM in older files
            df = pd.read_csv(filepath, encoding="utf-8-sig", low_memory=False)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Ensure columns are uppercase and clean
            df.columns = [col.replace('\ufeff', '').upper() for col in df.columns]
            
            # Clean string columns: strip whitespaces
            for col in df.select_dtypes(['object']).columns:
                df[col] = df[col].astype(str).str.strip()
            
            # Filtrar filas que contengan "Se ignora" o "No especificado" en cualquier columna
            for col in df.columns:
                df = df[~df[col].astype(str).str.strip().str.lower().isin(['se ignora', 'no especificado'])]
            
            # Filtrar horas y meses inválidos ('99' suele representar valores ignorados)
            if 'ID_HORA' in df.columns:
                df = df[df['ID_HORA'].astype(str) != '99']
            if 'MES' in df.columns:
                df = df[df['MES'].astype(str) != '99']
                
            # Convert numeric columns to numeric types safely
            numeric_cols = ['CONDMUERTO', 'CONDHERIDO', 'PASAMUERTO', 'PASAHERIDO',
                           'PEATMUERTO', 'PEATHERIDO', 'CICLMUERTO', 'CICLHERIDO',
                           'OTROMUERTO', 'OTROHERIDO', 'NEMUERTO', 'NEHERIDO']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

            # Output path
            out_file = os.path.join(output_dir, filename.replace('.csv', '.parquet'))
            df.to_parquet(out_file, index=False)
            return f"Procesado: {filename}"
        except Exception as e:
            return f"Error procesando {filename}: {str(e)}"

    files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    futures = [process_file.remote(f) for f in files]
    
    results = ray.get(futures)
    for r in results:
        print(r)
        
    end_time = time.time()
    print(f"Conversión a Parquet finalizada en {end_time - start_time:.2f} segundos.")
    ray.shutdown()

if __name__ == "__main__":
    process_csv_to_parquet()
