# app/streamlit_app.py
"""
Streamlit UI for the AI Resume–Job Matcher (Phase 1: Parsing).
- Upload a resume (PDF/DOCX) or use a sample.
- Paste a job description or use a sample .txt.
- See the first lines of parsed, normalized text.
"""

from __future__ import annotations

# --- Ensure we can import from the sibling 'src' package ----------------------
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# --- Third-party imports ------------------------------------------------------
import pathlib
import tempfile
import streamlit as st

# Helpful message if required parsing libs are missing
_missing = []
try:
    import fitz  # PyMuPDF
except Exception:
    _missing.append("pymupdf")

try:
    from docx import Document  # python-docx
except Exception:
    _missing.append("python-docx")

# --- Local imports ------------------------------------------------------------
from src.parsing import parse_resume, parse_job  # noqa: E402


# --- Page config --------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume–Job Matcher",
    page_icon="📄",
    layout="centered",
)

st.title("📄 AI Resume–Job Matcher — Phase 1: Parsing")

if _missing:
    st.warning(
        "Missing packages: **{}**. Install them with:\n\n"
        "`pip install {}`".format(", ".join(_missing), " ".join(_missing))
    )


# --- Controls -----------------------------------------------------------------
st.write(
    "Upload a resume (PDF/DOCX) and paste a Job Description, or use the sample files."
)

resume_file = st.file_uploader("Upload resume (PDF/DOCX)", type=["pdf", "docx"])
jd_text = st.text_area("Paste job description (optional if using sample JD)", height=180)

col1, col2 = st.columns(2)
with col1:
    use_sample_resume = st.checkbox("Use sample resume from data/samples", value=False)
with col2:
    use_sample_jd = st.checkbox("Use sample JD from data/samples", value=True)

run = st.button("Parse")


# --- Helpers ------------------------------------------------------------------
def _save_upload_to_temp(upload) -> pathlib.Path:
    """Save an uploaded file-like object to a NamedTemporaryFile and return its path."""
    suffix = ""
    if upload and "." in upload.name:
        suffix = "." + upload.name.rsplit(".", 1)[-1].lower()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(upload.read())
    tmp.flush()
    return pathlib.Path(tmp.name)


# --- Action -------------------------------------------------------------------
if run:
    try:
        # --- Resolve resume path ---
        if use_sample_resume:
            # You can change to sample_resume.docx if that's what you have
            resume_path = pathlib.Path("data/samples/sample_resume.pdf")
            if not resume_path.exists():
                # fallback to docx if pdf sample not found
                alt = pathlib.Path("data/samples/sample_resume.docx")
                if alt.exists():
                    resume_path = alt
                else:
                    raise FileNotFoundError(
                        "No sample resume found in data/samples "
                        "(expected sample_resume.pdf or sample_resume.docx)."
                    )
        else:
            if not resume_file:
                st.error("Please upload a resume or check 'Use sample resume'.")
                st.stop()
            resume_path = _save_upload_to_temp(resume_file)

        # --- Parse resume ---
        parsed_resume = parse_resume(resume_path)

        # --- Resolve JD source ---
        if use_sample_jd and not jd_text.strip():
            sample_jd_path = pathlib.Path("data/samples/sample_jd.txt")
            if not sample_jd_path.exists():
                raise FileNotFoundError(
                    "No sample JD found (expected data/samples/sample_jd.txt)."
                )
            parsed_jd = parse_job(str(sample_jd_path))
        else:
            if not jd_text.strip():
                st.warning(
                    "No JD text provided; parsing will show an empty JD. "
                    "You can enable 'Use sample JD' to try with a sample."
                )
            parsed_jd = parse_job(jd_text)

        # --- Display results ---
        st.success("Parsed successfully!")

        st.subheader("Resume (first 40 lines)")
        resume_preview = "\n".join(parsed_resume.text.splitlines()[:40]) or "(empty)"
        st.code(resume_preview)

        st.subheader("Job Description (first 40 lines)")
        jd_preview = "\n".join(parsed_jd.text.splitlines()[:40]) or "(empty)"
        st.code(jd_preview)

        # Meta (handy for debugging during development)
        with st.expander("Show metadata"):
            st.json(
                {
                    "resume_meta": parsed_resume.meta,
                    "jd_meta": parsed_jd.meta,
                    "resume_chars": len(parsed_resume.text),
                    "jd_chars": len(parsed_jd.text),
                }
            )

    except Exception as e:
        st.error(f"Parsing failed: {e}")
        st.stop()
else:
    st.info(
        "Click **Parse** after uploading a resume and pasting a JD, "
        "or enable the sample checkboxes."
    )
