import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Snowflake credentials
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")

# Use ACCOUNTADMIN role explicitly
SNOWFLAKE_ROLE = "ACCOUNTADMIN"

# Snowflake config
SNOWFLAKE_WAREHOUSE = "MY_WAREHOUSE"
SNOWFLAKE_DATABASE = "MY_DATABASE"
SNOWFLAKE_SCHEMA = "MY_SCHEMA"
TABLE = "WIKI_CHUNKS"
EMBED_MODEL = "snowflake-arctic-embed-l-v2.0"

# Connect to Snowflake
def create_snowflake_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        role=SNOWFLAKE_ROLE,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

# Setup Snowflake objects
def setup_snowflake_objects(conn):
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE WAREHOUSE IF NOT EXISTS {SNOWFLAKE_WAREHOUSE}")
        print(f"✅ Warehouse {SNOWFLAKE_WAREHOUSE} is ready.")
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {SNOWFLAKE_DATABASE}")
        print(f"✅ Database {SNOWFLAKE_DATABASE} is ready.")
        cur.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
        print(f"✅ Switched to database {SNOWFLAKE_DATABASE}")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SNOWFLAKE_SCHEMA}")
        print(f"✅ Schema {SNOWFLAKE_SCHEMA} is ready.")
        cur.execute(f"USE WAREHOUSE {SNOWFLAKE_WAREHOUSE}")
        cur.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")
        print(f"✅ Switched to schema {SNOWFLAKE_SCHEMA}")

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE} (
                chunk_text STRING,
                embedding VECTOR(FLOAT, 1024)
            )
        """)
        print(f"✅ Table {TABLE} is ready.")
    except Exception as e:
        print(f"❌ Setup error: {e}")
    finally:
        cur.close()

# Escape single quotes for SQL
def escape_sql_string(s):
    return s.replace("'", "''")

# Chunk the text into pieces
def chunk_text(text, chunk_size=1000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Embed and upload to Snowflake
def embed_and_upload_chunks(conn, chunks):
    cur = conn.cursor()
    for i, chunk in enumerate(chunks):
        try:
            escaped_chunk = escape_sql_string(chunk)
            query = f"""
                INSERT INTO {TABLE} (chunk_text, embedding)
                SELECT '{escaped_chunk}',
                       SNOWFLAKE.CORTEX.EMBED_TEXT_1024(
                           '{EMBED_MODEL}',
                           '{escaped_chunk}'
                       )
            """
            cur.execute(query)
            print(f"✅ Chunk {i} uploaded successfully.")
        except Exception as e:
            print(f"❌ Failed to embed chunk {i}: {e}")
    cur.close()

# Load text from local file
def load_text_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()

# Main workflow
def main():
    conn = create_snowflake_connection()
    setup_snowflake_objects(conn)
    #text_file_path = r'F:\wikibase-cortex-assistant\data\llama_summary.txt'
    text_file_path = r'F:\wikibase-cortex-assistant\data\articles\llama_language_model.txt'
    text = load_text_file(text_file_path)
    chunks = chunk_text(text)
    print(f"✅ Chunked text into {len(chunks)} chunks.")
    embed_and_upload_chunks(conn, chunks)
    conn.close()

if __name__ == "__main__":
    main()
