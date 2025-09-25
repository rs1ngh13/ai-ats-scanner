import streamlit as st

st.set_page_config(page_title="AI ATS Scanner", page_icon="📄", layout="centered")

# Big title at the top of the page
st.title("AI ATS Scanner")

# Short status text so users know Phase 0 is just a scaffold
st.write("Phase 0 scaffold is ready. Next steps: parsing & embeddings.")

# Upload widget to accept resume files (PDF or Word)
resume_file = st.file_uploader("Upload resume (PDF/DOCX)", type=["pdf", "docx"])

# Multiline input box where a user can paste a job description
jd_text = st.text_area("Paste job description")

# A button that’s intentionally disabled during Phase 0
if st.button("Run (disabled while in Phase 0)", disabled=True):
    # If someone clicks, show an info message explaining what’s next
    st.info("Implement Phase 1–3 first.")
