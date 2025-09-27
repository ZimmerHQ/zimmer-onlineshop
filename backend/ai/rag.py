from typing import List, Dict, Any
from sqlalchemy.orm import Session
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from database import SessionLocal
from services import product_service as PS

# In-memory singleton (rebuild on demand)
_vector = None
_index_data = None

def build_product_docs(db: Session) -> List[Dict[str, Any]]:
    items = PS.search_products(db, q=None, code=None, category_id=None, limit=10000)
    docs = []
    for p in items or []:
        desc = getattr(p, "description", "") or ""
        labels = getattr(p, "labels", []) or []
        attrs = getattr(p, "attributes", {}) or {}
        text = (
            f"نام: {getattr(p,'name','')}\n"
            f"کد: {getattr(p,'code','')}\n"
            f"قیمت: {getattr(p,'price',0)}\n"
            f"موجودی: {getattr(p,'stock',0)}\n"
            f"برچسب‌ها: {', '.join(labels) if isinstance(labels, list) else labels}\n"
            f"ویژگی‌ها: {attrs}\n"
            f"توضیحات: {desc}\n"
        )
        docs.append({"id": int(p.id), "code": getattr(p,"code",""), "text": text})
    return docs

def ensure_vector():
    global _vector, _index_data
    if _vector is not None:
        return _vector
    embeddings = OpenAIEmbeddings()  # uses OPENAI_API_KEY
    with SessionLocal() as db:
        docs = build_product_docs(db)
    _index_data = docs
    texts = [d["text"] for d in docs]
    metadatas = [{"id": d["id"], "code": d["code"]} for d in docs]
    _vector = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
    return _vector

def search_similar(query: str, k: int = 5) -> List[Dict[str, Any]]:
    vect = ensure_vector()
    results = vect.similarity_search_with_score(query, k=k)
    out = []
    for doc, score in results:
        md = doc.metadata or {}
        out.append({"id": md.get("id"), "code": md.get("code"), "snippet": doc.page_content[:500], "score": float(score)})
    return out

def rebuild_index():
    global _vector
    _vector = None
    ensure_vector()
