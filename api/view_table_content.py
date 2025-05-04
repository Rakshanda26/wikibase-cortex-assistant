import os
import snowflake.connector
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Snowflake credentials
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_ROLE = "ACCOUNTADMIN"

# Snowflake config
SNOWFLAKE_WAREHOUSE = "MY_WAREHOUSE"
SNOWFLAKE_DATABASE = "MY_DATABASE"
SNOWFLAKE_SCHEMA = "MY_SCHEMA"
TABLE = "WIKI_CHUNKS"

# Connect to Snowflake
def create_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            role=SNOWFLAKE_ROLE,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA
        )
        print(f"✅ Connected to Snowflake Database: {SNOWFLAKE_DATABASE}, Schema: {SNOWFLAKE_SCHEMA}")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to Snowflake: {e}")
        return None

# Fetch data and save to CSV
def fetch_and_save_dataframe(conn):
    if not conn:
        print("❌ Connection not established.")
        return
    cur = conn.cursor()
    try:
        print("🔍 Fetching rows from Snowflake...")
        fully_qualified_table_name = f"{SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{TABLE}"
        query = f"SELECT chunk_text FROM {fully_qualified_table_name} LIMIT 12"
        cur.execute(query)
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        print(f"✅ Fetched {len(rows)} rows.")
        df = pd.DataFrame(rows, columns=column_names)
        # Save DataFrame to CSV
        output_path = "output.csv"
        df.to_csv(output_path, index=False)
        print(f"✅ Data saved to CSV: {output_path}")
    except Exception as e:
        print(f"❌ Failed to fetch or save data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if cur:
            cur.close()

# Main function
def main():
    conn = create_snowflake_connection()
    if conn:
        fetch_and_save_dataframe(conn)
        conn.close()

if __name__ == "__main__":
    main()
