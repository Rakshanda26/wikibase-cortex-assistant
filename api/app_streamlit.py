import os
import snowflake.connector
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# Snowflake credentials
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_ROLE = "ACCOUNTADMIN"
SNOWFLAKE_WAREHOUSE = "MY_WAREHOUSE"
SNOWFLAKE_DATABASE = "MY_DATABASE"
SNOWFLAKE_SCHEMA = "MY_SCHEMA"
TABLE = "WIKI_CHUNKS"
EMBED_MODEL = "snowflake-arctic-embed-l-v2.0"

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

def get_best_chunk(question):
    conn = create_snowflake_connection()
    cur = conn.cursor()
    try:
        # Escape single quotes
        safe_question = question.replace("'", "''")

        query = f"""
            WITH query AS (
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024('{EMBED_MODEL}', '{safe_question}') AS query_embedding
            )
            SELECT chunk_text
            FROM {TABLE} AS w
            CROSS JOIN query
            ORDER BY VECTOR_INNER_PRODUCT(w.embedding, query_embedding) DESC
            LIMIT 1
        """
        cur.execute(query)
        result = cur.fetchone()
        return result[0] if result else "No relevant information found."
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        cur.close()
        conn.close()

# --- Streamlit UI ---
st.title("📚 WikiBase Cortex Assistant (Streamlit RAG)")
st.write("Ask your question and get an answer based on Wikipedia content!")

question = st.text_input("Enter your question:")
if question:
    with st.spinner("Searching..."):
        answer = get_best_chunk(question)
    st.markdown("### Answer:")
    st.write(answer)
