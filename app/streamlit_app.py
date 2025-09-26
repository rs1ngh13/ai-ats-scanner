# app/streamlit_app.py
"""
Streamlit UI for the AI Resume–Job Matcher (Phase 2: Embeddings).
"""

from __future__ import annotations
import os, sys, pathlib, tempfile
import streamlit as st

# --- ensure repo root is on sys.path ---
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Local imports
from src.parsing import parse_resume, parse_job
from src.embeddings import embed_and_pool
from src.scoring import score_match


# ------------------- UI CONFIG -------------------
st.set_page_config(page_title="AI Resume–Job Matcher", page_icon="📄", layout="centered")
st.title("📄 AI Resume–Job Matcher — Phase 2: Embeddings")

st.write("Upload a resume and paste a job description (or use sample files).")


# ------------------- HELPERS -------------------
def _save_upload_to_temp(upload) -> pathlib.Path:
    suffix = ""
    if upload and "." in upload.name:
        suffix = "." + upload.name.rsplit(".", 1)[-1].lower()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(upload.read())
    tmp.flush()
    return pathlib.Path(tmp.name)


# ------------------- CONTROLS -------------------
resume_file = st.file_uploader("Upload resume (PDF/DOCX)", type=["pdf", "docx"])
jd_text = st.text_area("Paste job description (or leave blank and test with a sample)", height=180)

col1, col2 = st.columns(2)
with col1:
    use_sample_resume = st.checkbox("Use sample resume", value=False)
with col2:
    use_sample_jd = st.checkbox("Use sample JD", value=True)

# Embedding model choice
model_choice = st.selectbox(
    "Embedding model",
    [
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/all-mpnet-base-v2",
        "intfloat/e5-large-v2",
        "BAAI/bge-large-en-v1.5",
    ],
    index=1,  # default = mpnet
)

pooling = st.radio("Pooling strategy", ["mean", "max"], horizontal=True, index=0)

run = st.button("Parse & Score")


# ------------------- ACTION -------------------
if run:
    try:
        # Resume
        if use_sample_resume:
            resume_path = pathlib.Path("data/samples/sample_resume_ml_engineer_formatted.pdf")
            if not resume_path.exists():
                raise FileNotFoundError("Sample resume not found in data/samples/")
        else:
            if not resume_file:
                st.error("Upload a resume or use the sample.")
                st.stop()
            resume_path = _save_upload_to_temp(resume_file)

        parsed_resume = parse_resume(resume_path)

        # JD
        if use_sample_jd and not jd_text.strip():
            jd_path = pathlib.Path("data/samples/sample_jd_machine_learning_engineer.txt")
            if not jd_path.exists():
                raise FileNotFoundError("Sample JD not found in data/samples/")
            parsed_jd = parse_job(str(jd_path))
        else:
            parsed_jd = parse_job(jd_text)

        # Embeddings + score
        with st.spinner("Computing embeddings & score..."):
            resume_vec = embed_and_pool(parsed_resume.text, model_name=model_choice, pool=pooling, is_query=False)
            jd_vec = embed_and_pool(parsed_jd.text, model_name=model_choice, pool=pooling, is_query=True)
            results = score_match(resume_vec, jd_vec)

        st.subheader("Match Score")
        st.metric(label="Cosine Similarity", value=f"{results['embedding_sim']:.3f}")
        st.progress(max(0.0, min(1.0, (results['embedding_sim'] + 1) / 2)))

    except Exception as e:
        st.error(f"Parsing or scoring failed: {e}")
else:
    st.info("Click **Parse & Score** after uploading files or selecting samples.")