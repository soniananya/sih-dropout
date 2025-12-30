import os
from glob import glob

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# -------- CONFIG --------
KB_DIR = "./kb_texts"
PERSIST_DIR = "./chroma_univ_kb"
COLLECTION_NAME = "university_kb"

# Gemini setup
from google.generativeai import GenerativeModel, configure

from dotenv import load_dotenv
import os
from google.generativeai import configure, GenerativeModel

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

configure(api_key=GEMINI_API_KEY)

GEMINI_MODEL = GenerativeModel("gemini-2.5-flash-lite")



# -------- LOAD TXT DOCS --------
def load_txt_documents(kb_dir: str):
    docs = []
    txt_files = glob(os.path.join(kb_dir, "*.txt"))
    if not txt_files:
        raise RuntimeError(f"No .txt files found in {kb_dir}")

    for path in txt_files:
        loader = TextLoader(path, encoding="utf-8")
        loaded = loader.load()

        filename = os.path.basename(path)
        base, _ = os.path.splitext(filename)

        for doc in loaded:
            doc.metadata["source"] = filename
            doc.metadata["doc_id"] = base

        docs.extend(loaded)

    return docs


# -------- BUILD VECTORSTORE --------
def build_vectorstore(docs):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vs = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
    )

    return vs


# -------- GEMINI ANSWERING --------
def get_gemini_answer(context: str, question: str) -> str:
    prompt = f"""
You are a student-support assistant.
Use ONLY the information in the context below to answer the question.
If the answer is not in the context, say: "Information not available in context."

Context:
{context}

Question:
{question}

Answer clearly:
"""
    response = GEMINI_MODEL.generate_content(prompt)
    return response.text


# -------- RAG PIPELINE (FIXED) --------
def get_rag_answer(vectorstore, query: str, k: int = 3):
    # FIXED: Use similarity_search instead of retriever.invoke
    docs = vectorstore.similarity_search(query, k=k)

    combined = "\n\n".join([d.page_content for d in docs])
    final_answer = get_gemini_answer(combined, query)

    return docs, combined, final_answer


# -------- MAIN --------
def main():
    print(f"Loading .txt docs from: {KB_DIR}")
    docs = load_txt_documents(KB_DIR)
    print(f"Loaded {len(docs)} documents.")

    print("Building Chroma vector store...")
    vs = build_vectorstore(docs)

    print(f"Chroma DB created at: {PERSIST_DIR}")
    print(f"Collection name: {COLLECTION_NAME}")

    query = "What benefits can a highly depressed student avail?"

    print(f"\nRunning RAG for query: {query}")
    docs, context_text, final_answer = get_rag_answer(vs, query)

    for i, d in enumerate(docs, 1):
        print(f"\n--- Result {i} (source={d.metadata.get('source')}) ---")
        print(d.page_content[:300], "...")

    print("\n\nCombined RAG Context:\n", context_text[:500], "...")
    print("\n\nGemini Answer:\n", final_answer)


if __name__ == "__main__":
    main()