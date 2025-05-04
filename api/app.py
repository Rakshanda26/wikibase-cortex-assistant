import os
import snowflake.connector
from dotenv import load_dotenv
from flask import Flask, render_template, request

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

# Escape single quotes for SQL
def escape_sql_string(s):
    return s.replace("'", "''")

# Flask app setup
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]

    try:
        conn = create_snowflake_connection()
        cur = conn.cursor()

        # Escape the question for SQL safety
        safe_question = escape_sql_string(question)

        # SQL query using vector inner product (no SIMILARITY)
        query = f"""
            WITH query AS (
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024(
                    '{EMBED_MODEL}', '{safe_question}'
                ) AS query_embedding
            )
            SELECT w.chunk_text
            FROM {TABLE} AS w
            CROSS JOIN query
            ORDER BY VECTOR_INNER_PRODUCT(w.embedding, query.query_embedding) DESC
            LIMIT 1;
        """

        cur.execute(query)
        result = cur.fetchone()

        if result:
            answer = result[0]
        else:
            answer = "No relevant information found."

        cur.close()
        conn.close()
    except Exception as e:
        answer = f"Error while fetching answer: {str(e)}"

    return render_template("index.html", question=question, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
