# ui/rag.py
"""
Thin orchestration layer over backend_multimodal.py. The retrieval +
generation logic here is moved verbatim from the original single-file
streamlit_app_multilingual.py (same hybrid-search fallback, same similarity
threshold, same conversation-history window) — not rewritten — so behavior
is unchanged. This is the one place both the Home quick-ask and the AI
Tutor chat call into, so there's a single implementation of "ask EduRAG".
"""
import os

import streamlit as st

from backend_multimodal import (
    detect_language,
    generate_quiz_questions,
    get_chapter_context,
    get_llm,
    hybrid_search,
    load_models,
    preprocess_query,
    process_image_input,
    text_to_speech,
)

__all__ = [
    "get_models", "get_question_llm", "ask_question", "generate_questions_for",
    "normalize_llm_output", "friendly_error_message",
    "process_image_input", "text_to_speech", "detect_language",
]


@st.cache_resource(show_spinner="Loading EduRAG models…")
def get_models():
    """Cached so embeddings/vector store/LLM client load exactly once per
    server process, not on every rerun/navigation click."""
    return load_models()


@st.cache_resource(show_spinner=False)
def get_question_llm():
    return get_llm(temperature=0.5)


def normalize_llm_output(result):
    if isinstance(result, str):
        return result
    if hasattr(result, "content"):
        content = result.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("text"):
                    parts.append(item["text"])
                elif isinstance(item, str):
                    parts.append(item)
            normalized = "\n".join(parts).strip()
            if normalized:
                return normalized
    return str(result)


def friendly_error_message(exc) -> str:
    err_text = str(exc)
    if "PERMISSION_DENIED" in err_text and "leaked" in err_text.lower():
        return (
            "Gemini API request failed: the current GOOGLE_API_KEY is blocked "
            "because it was reported as leaked. Generate a new key, update `.env`, "
            "and restart the app."
        )
    if "PERMISSION_DENIED" in err_text:
        return (
            "Gemini API request was denied. Verify GOOGLE_API_KEY and model access "
            "permissions, then restart the app."
        )
    if "FileNotFoundError" in err_text or "not found" in err_text.lower():
        return "EduRAG's knowledge base isn't loaded. Please check the setup and restart."
    return "EduRAG couldn't process that request right now. Please try again."


def ask_question(prompt_text: str, image_data=None) -> dict:
    """
    Core RAG pipeline. Assumes the caller has ALREADY appended the current
    user turn to st.session_state.messages (same convention as the original
    implementation, which excludes the just-appended message when building
    conversation_history).

    Returns {"response": str, "sources": list[dict]}.
    """
    vectorstore, chain = get_models()
    if vectorstore is None or chain is None:
        raise RuntimeError("Backend models are not loaded.")

    query_text = prompt_text or "Please analyze this image and explain what you see"
    original_query, expanded_query = preprocess_query(query_text)

    # 1. Hybrid search with graceful fallback
    try:
        docs_with_scores = hybrid_search(vectorstore, original_query, k=5)
    except Exception:
        docs_with_scores = vectorstore.similarity_search_with_score(original_query, k=5)

    # 2. If not similar enough, broaden with the expanded query
    if docs_with_scores and docs_with_scores[0][1] > 1.0:
        try:
            expanded_docs = hybrid_search(vectorstore, expanded_query, k=3)
        except Exception:
            expanded_docs = vectorstore.similarity_search_with_score(expanded_query, k=3)
        all_docs = docs_with_scores + expanded_docs
        seen_content = set()
        unique_docs = []
        for doc, score in all_docs:
            content_hash = hash(doc.page_content[:100])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append((doc, score))
        docs_with_scores = sorted(unique_docs, key=lambda x: x[1])[:5]

    # 3. Filter by similarity threshold, falling back to top-3
    similarity_threshold = 1.2
    relevant_docs = [doc for doc, score in docs_with_scores if score < similarity_threshold]
    if not relevant_docs:
        relevant_docs = [doc for doc, score in docs_with_scores[:3]]

    # 4. Build context
    context_parts = []
    for i, doc in enumerate(relevant_docs):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")
        context_parts.append(f"Source {i+1} ({source}, Page {page}):\n{doc.page_content}")
    context = "\n\n".join(context_parts)

    # 5. Conversation history (last 3 exchanges, excluding the just-appended turn)
    conversation_history = ""
    messages = st.session_state.get("messages", [])
    if len(messages) > 1:
        recent_messages = messages[-6:]
        history_parts = []
        for msg in recent_messages[:-1]:
            role = "Student" if msg["role"] == "user" else "Assistant"
            content = msg["content"]
            if msg.get("has_image"):
                content += " [Student also shared an image]"
            history_parts.append(f"{role}: {content}")
        conversation_history = "\n".join(history_parts)

    # 6. Generate
    result = chain.invoke({
        "conversation_history": conversation_history,
        "context": context,
        "question": original_query,
    })
    response_text = normalize_llm_output(result)

    # 7. Sources
    sources = []
    for doc in relevant_docs:
        source_file = os.path.basename(doc.metadata.get("source", "Unknown"))
        source_info = {"source": source_file, "page": doc.metadata.get("page", "N/A")}
        if source_info not in sources:
            sources.append(source_info)

    return {"response": response_text, "sources": sources}


def generate_questions_for(chapter_file: str, chapter_title: str, difficulty: str, num_questions: int):
    """Grounded MCQ generation for Practice/Quiz, scoped to one real chapter."""
    vectorstore, _ = get_models()
    llm = get_question_llm()
    context = get_chapter_context(vectorstore, chapter_file)
    return generate_quiz_questions(llm, context, chapter_title, difficulty, num_questions)
