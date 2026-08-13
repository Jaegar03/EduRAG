# backend_multimodal.py
"""
Backend logic for EduRAG Multilingual: model loading, search, and preprocessing functions.
"""
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from PIL import Image
import io
import base64
from gtts import gTTS
from langdetect import detect, LangDetectException

# --- CONFIGURATION ---
VECTOR_STORE_PATH = "faiss_index"
MODEL_NAME = "all-MiniLM-L6-v2"
GEMINI_MODEL_NAME = "gemini-2.5-flash"

load_dotenv()

def load_models():
    # from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    if not os.path.exists(VECTOR_STORE_PATH):
        raise FileNotFoundError(
            f"FAISS index not found at '{VECTOR_STORE_PATH}'. "
            "Please run 'python ingest.py' first."
        )
    
    # Load FAISS index
    vectorstore = FAISS.load_local(
        folder_path=VECTOR_STORE_PATH,
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )

    api_key = (os.getenv("GOOGLE_API_KEY") or "").strip().strip('"').strip("'")
    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY is missing. Add it to .env as GOOGLE_API_KEY=your_key"
        )
    
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        temperature=0.3,
        google_api_key=api_key
    )
    prompt_template = """
You are an expert educational assistant helping students with NCERT textbooks. You are having a conversation with a student and should respond in a helpful, conversational manner.

Instructions:
1. Use the provided context from textbooks to answer questions
2. Reference previous parts of the conversation when relevant
3. Be conversational and encouraging
4. If no direct answer exists in the context, look for related information
5. Mention chapter titles, sections, or topics when they help explain concepts
6. Only if absolutely no relevant information exists, suggest how the student might rephrase their question
7. Keep your responses engaging and educational

Previous conversation:
{conversation_history}

Context from textbook(s):
{context}

Student's Question: {question}

Your Response:
"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["conversation_history", "context", "question"])
    chain = PROMPT | llm
    return vectorstore, chain

def hybrid_search(vectorstore, query, k=5):
    """
    Perform hybrid search combining semantic and keyword-based retrieval.
    """
    semantic_docs = vectorstore.similarity_search_with_score(query, k=k)
    all_docs = vectorstore.get() if hasattr(vectorstore, "get") else {}
    keyword_matches = []
    query_words = set(query.lower().split())
    if 'documents' in all_docs and 'metadatas' in all_docs:
        for i, (doc_text, metadata) in enumerate(zip(all_docs['documents'], all_docs['metadatas'])):
            doc_words = set(doc_text.lower().split())
            overlap = len(query_words.intersection(doc_words))
            if overlap > 0:
                from langchain_core.documents import Document
                doc = Document(page_content=doc_text, metadata=metadata)
                score = 1.0 / (overlap + 1)
                keyword_matches.append((doc, score))
    all_results = semantic_docs + keyword_matches
    seen_content = set()
    unique_results = []
    for doc, score in all_results:
        content_hash = hash(doc.page_content[:100])
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            unique_results.append((doc, score))
    return sorted(unique_results, key=lambda x: x[1])[:k]

def preprocess_query(query):
    processed_query = query.lower().strip()
    physics_synonyms = {
        "chapters": ["topics", "sections", "units"],
        "physics": ["physical science", "mechanics", "motion"],
        "energy": ["power", "force", "work"],
        "conservation": ["preservation", "constant"],
        "law": ["principle", "rule", "theorem"],
        "motion": ["movement", "kinematics"],
        "electricity": ["electric", "electrical", "current"],
        "magnetism": ["magnetic", "magnet"],
        "light": ["optics", "optical", "rays"],
        "waves": ["wave", "vibration", "oscillation"]
    }
    query_terms = processed_query.split()
    expanded_terms = []
    for term in query_terms:
        expanded_terms.append(term)
        for key, synonyms in physics_synonyms.items():
            if term in key or key in term:
                expanded_terms.extend(synonyms)
    expanded_query = " ".join(expanded_terms)
    return query, expanded_query

def process_image_input(uploaded_image):
    if uploaded_image is not None:
        try:
            image = Image.open(uploaded_image)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            img_base64 = base64.b64encode(img_byte_arr).decode()
            return {
                "image": image,
                "base64": img_base64,
                "description": "User uploaded an image related to their question"
            }
        except Exception as e:
            return None
    return None

def detect_language(text):
    """
    Detect the language of the given text.
    Returns language code (default: 'en' if detection fails).
    """
    try:
        # Use langdetect to detect language
        lang_code = detect(text)
        return lang_code
    except LangDetectException:
        # If detection fails, default to English
        return 'en'
    except Exception:
        return 'en'

def get_tts_language_code(lang_code):
    """
    Map detected language code to gTTS supported language code.
    gTTS supports many languages but uses specific codes.
    """
    # Language code mapping for gTTS
    tts_language_map = {
        'en': 'en',  # English
        'hi': 'hi',  # Hindi
        'bn': 'bn',  # Bengali
        'te': 'te',  # Telugu
        'mr': 'mr',  # Marathi
        'ta': 'ta',  # Tamil
        'ur': 'ur',  # Urdu
        'gu': 'gu',  # Gujarati
        'kn': 'kn',  # Kannada
        'ml': 'ml',  # Malayalam
        'es': 'es',  # Spanish
        'fr': 'fr',  # French
        'de': 'de',  # German
        'zh': 'zh',  # Chinese (Simplified)
        'zh-cn': 'zh',  # Chinese (Simplified)
        'ar': 'ar',  # Arabic
        'it': 'it',  # Italian
        'ja': 'ja',  # Japanese
        'ko': 'ko',  # Korean
        'pt': 'pt',  # Portuguese
        'ru': 'ru',  # Russian
    }
    
    # Normalize language code to lowercase
    lang_code = lang_code.lower() if lang_code else 'en'
    
    # Return mapped language code or default to English
    return tts_language_map.get(lang_code, 'en')

def text_to_speech(text, lang_code=None):
    """
    Convert text to speech using gTTS.
    
    Args:
        text: The text to convert to speech
        lang_code: Optional language code. If not provided, will auto-detect.
    
    Returns:
        BytesIO object containing the audio data, or None if conversion fails.
    """
    if text is None:
        return None
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()
    if not text:
        return None

    try:
        # If language code not provided, detect it
        if lang_code is None:
            detected_lang = detect_language(text)
            lang_code = get_tts_language_code(detected_lang)
        else:
            lang_code = get_tts_language_code(lang_code)
        
        # Create gTTS object
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Save to BytesIO buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return audio_buffer
    except Exception as e:
        raise RuntimeError(f"TTS generation failed: {str(e)}") from e


# --- ADDITIONS BELOW: Practice/Quiz question generation ---------------------
# These are additive helpers used by the Practice and Quiz screens. They do
# not change any behavior of load_models()/hybrid_search()/etc. above.

def get_llm(temperature: float = 0.5):
    """
    Create a standalone Gemini client for auxiliary generation tasks (e.g.
    practice/quiz question writing) that don't use the conversational QA
    prompt/chain built inside load_models().
    """
    api_key = (os.getenv("GOOGLE_API_KEY") or "").strip().strip('"').strip("'")
    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY is missing. Add it to .env as GOOGLE_API_KEY=your_key"
        )
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        temperature=temperature,
        google_api_key=api_key,
    )


def get_chapter_context(vectorstore, source_filename, max_chunks=6):
    """
    Pull representative chunks for one specific source PDF (chapter) directly
    out of the vector store, to ground practice/quiz question generation in
    real textbook content. Returns "" if nothing is found for that file.

    Note: langchain's FAISS wrapper has no .get() (unlike Chroma), so this
    walks its docstore directly rather than reusing hybrid_search()'s
    Chroma-oriented all_docs pattern.
    """
    chunks = []
    docstore = getattr(vectorstore, "docstore", None)
    inner = getattr(docstore, "_dict", None) if docstore is not None else None
    if inner:
        for doc in inner.values():
            source = os.path.basename(doc.metadata.get("source", ""))
            if source == source_filename:
                chunks.append(doc.page_content)
    if not chunks:
        return ""
    # Spread the sample across the whole chapter rather than just its start.
    step = max(1, len(chunks) // max_chunks)
    sampled = chunks[::step][:max_chunks]
    return "\n\n".join(sampled)


def generate_quiz_questions(llm, context, chapter_label, difficulty="Medium", num_questions=5):
    """
    Generate multiple-choice questions grounded in real NCERT context using
    the Gemini LLM.

    Returns a list of dicts:
        {"question": str, "options": [str, str, str, str],
         "correct_index": int, "explanation": str}

    Raises ValueError if the model output could not be parsed into valid
    questions.
    """
    import json
    import re

    if not context.strip():
        raise ValueError(f"No indexed textbook content found for '{chapter_label}'.")

    prompt = f"""You are an expert NCERT Physics exam-question writer.
Using ONLY the textbook context below, write {num_questions} multiple-choice
questions about "{chapter_label}" at {difficulty} difficulty.

Textbook context:
{context}

Rules:
- Each question must have exactly 4 options.
- Exactly one option must be correct.
- Base every question strictly on the given context; do not invent facts outside it.
- Return ONLY a JSON array, no prose, no markdown fences, matching this schema:
[{{"question": "...", "options": ["...", "...", "...", "..."], "correct_index": 0, "explanation": "..."}}]
"""
    result = llm.invoke(prompt)
    raw = result.content if hasattr(result, "content") else str(result)
    if isinstance(raw, list):
        raw = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in raw)

    match = re.search(r"\[.*\]", raw, re.DOTALL)
    json_text = match.group(0) if match else raw

    try:
        questions = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse quiz questions from model output: {e}") from e

    validated = []
    for q in questions:
        if (
            isinstance(q, dict)
            and isinstance(q.get("question"), str)
            and isinstance(q.get("options"), list)
            and len(q["options"]) >= 2
            and isinstance(q.get("correct_index"), int)
            and 0 <= q["correct_index"] < len(q["options"])
        ):
            validated.append({
                "question": q["question"],
                "options": q["options"],
                "correct_index": q["correct_index"],
                "explanation": q.get("explanation", ""),
            })
    if not validated:
        raise ValueError("The model did not return any valid questions. Please try again.")
    return validated
