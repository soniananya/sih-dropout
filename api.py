from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rag import get_rag_answer, build_vectorstore, load_txt_documents
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

router = APIRouter()

# Global vectorstore (loaded once at startup)
vectorstore = None


class RAGRequest(BaseModel):
    query: str
    k: int = 3


class RAGResponse(BaseModel):
    query: str
    answer: str
    context: str
    sources: list


def get_vectorstore():
    """Initialize or return existing vectorstore"""
    global vectorstore

    if vectorstore is None:
        persist_dir = "./chroma_univ_kb"
        collection_name = "university_kb"

        # Check if vectorstore already exists
        if os.path.exists(persist_dir):
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            vectorstore = Chroma(
                collection_name=collection_name,
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
        else:
            # Build new vectorstore
            kb_dir = "./kb_texts"
            docs = load_txt_documents(kb_dir)
            vectorstore = build_vectorstore(docs)

    return vectorstore


@router.post("/rag", response_model=RAGResponse)
def rag_endpoint(request: RAGRequest):
    """
    RAG endpoint to answer questions based on knowledge base
    """
    try:
        # Get vectorstore
        vs = get_vectorstore()

        # FIXED: get_rag_answer returns 3 values: docs, combined, final_answer
        docs, combined, final_answer = get_rag_answer(vs, request.query, k=request.k)

        # Extract source information
        sources = [
            {
                "source": doc.metadata.get("source", "unknown"),
                "doc_id": doc.metadata.get("doc_id", "unknown"),
                "content_preview": doc.page_content[:200]
            }
            for doc in docs
        ]

        return RAGResponse(
            query=request.query,
            answer=final_answer,
            context=combined[:1000],  # Limit context in response
            sources=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing RAG query: {str(e)}")


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "vectorstore_loaded": vectorstore is not None}

# from fastapi import APIRouter
# from pydantic import BaseModel
#
# # --- import your existing code ---
# from rag import load_txt_documents, build_vectorstore, get_rag_answer, KB_DIR
#
# # router
# router = APIRouter()
#
# # Load Vectorstore once when API initializes
# docs = load_txt_documents(KB_DIR)
# vectorstore = build_vectorstore(docs)
#
#
# class RAGQuery(BaseModel):
#     query: str
#     k: int = 3
#
#
# @router.post("/rag")
# def rag_endpoint(payload: RAGQuery):
#     docs, combined = get_rag_answer(
#         vectorstore=vectorstore,
#         query=payload.query,
#         k=payload.k
#     )
#
#     return {
#         "query": payload.query,
#         "results": [
#             {
#                 "source": d.metadata.get("source"),
#                 "chunk": d.page_content
#             }
#             for d in docs
#         ],
#         "combined_text": combined
#     }
