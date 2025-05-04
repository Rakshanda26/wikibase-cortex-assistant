from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import snowflake.connector
from dotenv import load_dotenv

# Load env vars
load_dotenv()

app = FastAPI()

# Config
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_ROLE = "ACCOUNTADMIN"
SNOWFLAKE_WAREHOUSE = "MY_WAREHOUSE"
SNOWFLAKE_DATABASE = "MY_DATABASE"
SNOWFLAKE_SCHEMA = "MY_SCHEMA"
TABLE = "WIKI_CHUNKS"
EMBED_MODEL = "snowflake/snowflake-arctic-embed"
LLM_MODEL = "snowflake/snowflake-arctic"

# Request schema
class Question(BaseModel):
    question: str

# Connect to Snowflake
def create_conn():
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        role=SNOWFLAKE_ROLE,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

@app.post("/answer")
def answer_question(query: Question):
    conn = create_conn()
    cur = conn.cursor()
    try:
        user_q = query.question.replace("'", "''")

        # Embed the question
        cur.execute(f"""
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('{user_q}' USING PARAMETERS MODEL_NAME = '{EMBED_MODEL}')
        """)
        question_vector = cur.fetchone()[0]

        # Vector similarity search (top 3 matches)
        cur.execute(f"""
            SELECT chunk_text
            FROM {TABLE}
            ORDER BY chunk_text <-> %s
            LIMIT 3
        """, (question_vector,))
        top_chunks = [row[0] for row in cur.fetchall()]

        if not top_chunks:
            raise HTTPException(status_code=404, detail="No relevant context found.")

        context = "\n\n".join(top_chunks)
        prompt = f"""Context: {context}\n\nQuestion: {query.question}\nAnswer:"""

        # Generate answer using LLM
        cur.execute(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('{prompt}' USING PARAMETERS MODEL_NAME = '{LLM_MODEL}')
        """)
        answer = cur.fetchone()[0]

        return {"answer": answer.strip()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
