
conda create --name wikibase_cortex_env_0410 python=3.10 -y

pip install -r requirements.txt

Project Name : wikibase-cortex-assistant
FLOW :

User sends a question → FastAPI receives it → Embeds query using Snowflake Cortex → Retrieves top matching Wikipedia chunks from Snowflake using vector search → Sends context + question to Cortex LLM → Returns generated answer to user.


User sends a question
    ↓
FastAPI receives it (via endpoint in `api/main.py`)
    ↓
Query is embedded using Snowflake Cortex (handled in `cortex_handler.py`)
    ↓
Vector search in Snowflake retrieves top-matching Wikipedia chunks (via `snowflake_client.py`)
    ↓
Relevant chunks + original question sent to Cortex LLM
    ↓
Cortex generates an answer
    ↓
FastAPI returns the answer to the user




### ✅ **Embedding Flow in Snowflake Cortex (Query → Vector)**

Snowflake provides a built-in function for embeddings:

#### **Model Used for Embeddings:**
You’ll use:
```sql
CORTEX.EMBED_TEXT(<'text'> USING PARAMETERS MODEL_NAME = '<embedding-model>')
```

Example embedding call:
```sql
SELECT cortex.embed_text('Who is Marie Curie?' USING PARAMETERS MODEL_NAME = 'snowflake/snowflake-arctic-embed');
```

#### ✅ Recommended Embedding Model:
- `"snowflake/snowflake-arctic-embed"` (Optimized for RAG tasks, supported natively in Snowflake)
- Or: `"snowflake/embedding-ada"` (OpenAI Ada-like, if supported)

---

### 🔁 **How it Fits in the RAG Flow**

| Step                        | Detail                                                                 |
|-----------------------------|------------------------------------------------------------------------|
| 1. **User query**           | e.g., "Tell me about Newton’s laws"                                    |
| 2. **Embed query**          | Use `CORTEX.EMBED_TEXT` to convert query to vector                     |
| 3. **Search DB**            | Run **vector similarity search** on pre-embedded Wikipedia chunks      |
| 4. **Retrieve top-k**       | Select top matching chunks (e.g., via cosine distance)                 |
| 5. **Send to LLM**          | Combine question + retrieved context → send to `CORTEX.COMPLETE()`     |
| 6. **Generate answer**      | LLM generates final answer with better grounding/context               |

---

### 🧠 Summary
You are:
- Using **Cortex’s embedding models** (no local model needed).
- Relying on **Snowflake-managed embedding + vector search**, fully serverless.
- Supporting a clean **RAG architecture** with:
  - **Chunked documents** stored in Snowflake
  - **Query vector** matched against stored vectors
  - **Final answer** generated using LLM with context

User → FastAPI → Cortex Embed → Snowflake Vector Search → Context + Query → Cortex LLM → Answer → User

docker build -t streamlit-rag .