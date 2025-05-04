import os
import snowflake.connector
import streamlit as st
from dotenv import load_dotenv

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

# Escape single quotes
def escape_sql_string(s):
    return s.replace("'", "''")

# Chunk the text
def chunk_text(text, chunk_size=1000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Upload to Snowflake
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
            st.success(f"✅ Chunk {i + 1} uploaded.")
        except Exception as e:
            st.error(f"❌ Error uploading chunk {i + 1}: {e}")
    cur.close()

# Streamlit App
st.set_page_config(page_title="📚 WikiBase Cortex Assistant (Streamlit RAG)")
st.title("📚 WikiBase Cortex Assistant (Streamlit RAG)")
st.write("Ask your question and get an answer based on Wikipedia content!")

# Upload Section
uploaded_file = st.file_uploader("Upload a .txt file to ingest into Snowflake:", type=["txt"])
if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
    chunks = chunk_text(text)
    st.info(f"✅ File chunked into {len(chunks)} pieces.")

    if st.button("Embed & Upload to Snowflake"):
        conn = create_snowflake_connection()
        embed_and_upload_chunks(conn, chunks)
        conn.close()
        st.success("✅ All chunks embedded and uploaded!")

# Ask a Question Section
st.subheader("Enter your question:")
question = st.text_input("")

if question:
    try:
        safe_question = escape_sql_string(question)
        conn = create_snowflake_connection()
        cur = conn.cursor()

        query = f"""
            WITH query AS (
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024(
                    '{EMBED_MODEL}', '{safe_question}'
                ) AS query_embedding
            )
            SELECT chunk_text
            FROM {TABLE} AS w
            CROSS JOIN query
            ORDER BY VECTOR_INNER_PRODUCT(w.embedding, query_embedding) DESC
            LIMIT 1
        """
        cur.execute(query)
        result = cur.fetchone()
        answer = result[0] if result else "No relevant information found."

        cur.close()
        conn.close()

        st.subheader("Answer:")
        st.write(answer)
    except Exception as e:
        st.error(f"Error while fetching answer: {str(e)}")
