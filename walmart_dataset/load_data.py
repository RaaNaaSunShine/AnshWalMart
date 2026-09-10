import os
from pathlib import Path

import psycopg

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "dbname=wm_source_data user=wm_pipeline host=localhost port=5432",
)

# CSV files mapping to tables
csv_files = {
    "customers.csv": "ansh_walmart_source_csv_files.customers",
    "stores.csv": "ansh_walmart_source_csv_files.stores",
    "products.csv": "ansh_walmart_source_csv_files.products",
    "employees.csv": "ansh_walmart_source_csv_files.employees",
    "orders.csv": "ansh_walmart_source_csv_files.orders",
    "order_items.csv": "ansh_walmart_source_csv_files.order_items",
}

data_dir = Path(__file__).parent / "data"
conn = None

try:
    # Connect to the database
    conn = psycopg.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Load each CSV file into its corresponding table
    for csv_file, table_name in csv_files.items():
        csv_path = os.path.join(data_dir, csv_file)
        
        if os.path.exists(csv_path):
            print(f"Loading {csv_file} into {table_name}...")
            
            with open(csv_path, "r") as f:
                with cursor.copy(
                    f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
                ) as copy:
                    for chunk in f:
                        copy.write(chunk)
            
            conn.commit()
            print(f"✓ Successfully loaded {csv_file}")
        else:
            print(f"✗ File not found: {csv_path}")
    
    cursor.close()
    conn.close()
    print("\n✓ All data loaded successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    if conn is not None:
        conn.rollback()
        conn.close()
