import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai
import os

# -------------------------------
# Configure Gemini
# -------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="AI Agreement Risk Scanner (Google Gemini)",
    page_icon="📄",
)

st.title("📄 AI Agreement Risk Scanner")
st.caption("Powered by Google Gemini AI")

# -------------------------------
# Extract PDF Text
# -------------------------------
def extract_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text.strip()

# -------------------------------
# Gemini Risk Analysis
# -------------------------------
def analyze_with_gemini(text):
    prompt = f"""
You are a legal risk analyzer.

Analyze the agreement below and respond in this format:

1. Overall Risk Level (Low / Medium / High)
2. Risk Score (0-100)
3. Top 5 Risky Clauses (bullet points)
4. How this agreement can harm the user
5. Simple advice for the user

AGREEMENT:
{text}
"""
    response = model.generate_content(prompt)
    return response.text

# -------------------------------
# Upload PDF
# -------------------------------
uploaded_file = st.file_uploader("Upload Agreement PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text..."):
        text = extract_text(uploaded_file)

    if not text:
        st.error("No readable text found.")
    else:
        st.success("Text extracted")

        st.subheader("📜 Agreement Text")
        st.text_area("Content", text, height=250)

        if st.button("🔍 Analyze Agreement with AI"):
            with st.spinner("Analyzing with Google Gemini..."):
                analysis = analyze_with_gemini(text)

            st.subheader("⚠️ AI Risk Analysis")
            st.markdown(analysis)

st.markdown("---")
st.caption("Uses Google Gemini API | Educational Purpose Only")

