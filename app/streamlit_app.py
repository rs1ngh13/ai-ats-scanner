import streamlit as st
from src.parsing import parse_resume, parse_job
import tempfile
import pathlib

st.set_page_config(page_title="AI Resume–Job Matcher", page_icon="📄", layout="centered")
st.title("📄 AI Resume–Job Matcher (Phase 1: Parsing)")

resume_file = st.file_uploader("Upload resume (PDF/DOCX)", type=["pdf", "docx"])
jd_text = st.text_area("Paste job description (or leave blank and test with a sample)")

col1, col2 = st.columns(2)
with col1:
    use_sample_resume = st.checkbox("Use sample resume", value=False)
with col2:
    use_sample_jd = st.checkbox("Use sample JD", value=True)

if st.button("Parse"):
    try:
        # Resume source: uploaded or sample path
        if use_sample_resume:
            resume_path = pathlib.Path("data/samples/sample_resume.pdf")
        else:
            if not resume_file:
                st.error("Please upload a resume or check 'Use sample resume'.")
                st.stop()
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}")
            tmp.write(resume_file.read())
            tmp.flush()
            resume_path = pathlib.Path(tmp.name)

        parsed_resume = parse_resume(resume_path)

        # JD source: pasted or sample path
        if use_sample_jd and not jd_text.strip():
            parsed_jd = parse_job("data/samples/sample_jd.txt")
        else:
            parsed_jd = parse_job(jd_text)

        st.success("Parsed successfully!")
        st.subheader("Resume (first 40 lines)")
        st.code("\n".join(parsed_resume.text.splitlines()[:40]) or "(empty)")
        st.subheader("Job Description (first 40 lines)")
        st.code("\n".join(parsed_jd.text.splitlines()[:40]) or "(empty)")

    except Exception as e:
        st.error(f"Parsing failed: {e}")
