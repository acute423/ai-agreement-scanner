import streamlit as st
from pypdf import PdfReader

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="AI Agreement Risk Scanner",
    page_icon="📄",
    layout="centered"
)

st.title("📄 AI Agreement Risk Scanner")
st.write(
    "Upload any agreement or terms & conditions PDF. "
    "This tool will extract text and highlight potential risks."
)

# -------------------------------
# PDF Text Extraction
# -------------------------------
def extract_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()

# -------------------------------
# Risk Analysis (Rule-based)
# -------------------------------
def analyze_risks(text):
    risks = []

    risk_keywords = {
        "termination": "Agreement can be terminated without notice.",
        "no liability": "Company limits its responsibility.",
        "indemnify": "You may have to pay for company losses.",
        "auto-renew": "Agreement renews automatically.",
        "non-refundable": "Money paid cannot be recovered.",
        "jurisdiction": "Legal disputes restricted to a specific location.",
        "arbitration": "You give up the right to go to court.",
        "third party": "Your data may be shared with third parties.",
        "without notice": "Terms can change without informing you."
    }

    lower_text = text.lower()

    for keyword, explanation in risk_keywords.items():
        if keyword in lower_text:
            risks.append(explanation)

    risk_score = min(len(risks) * 10, 100)
    return risks, risk_score

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader(
    "Upload Agreement PDF",
    type=["pdf"]
)

if uploaded_file:
    with st.spinner("Extracting text from PDF..."):
        text = extract_text(uploaded_file)

    if not text:
        st.error("❌ No readable text found in this PDF.")
    else:
        st.success("✅ Text extracted successfully")

        st.subheader("📜 Extracted Agreement Text")
        st.text_area("Agreement Content", text, height=300)

        st.subheader("⚠️ Risk Analysis")
        risks, score = analyze_risks(text)

        if risks:
            for i, risk in enumerate(risks, start=1):
                st.warning(f"{i}. {risk}")
        else:
            st.success("No major risk keywords found.")

        st.subheader("📊 Overall Risk Score")
        st.progress(score)
        st.write(f"**Risk Level:** {score} / 100")

        if score >= 70:
            st.error("🚨 High Risk Agreement – Read Carefully!")
        elif score >= 40:
            st.warning("⚠️ Medium Risk Agreement")
        else:
            st.success("✅ Low Risk Agreement")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("🚀 AI Agreement Risk Scanner | Streamlit Cloud Ready")
