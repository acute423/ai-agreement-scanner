import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from sentence_transformers import SentenceTransformer, util

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI Agreement Risk Scanner", layout="wide")

st.title("📄 AI-Driven Agreement Risk Scanner")
st.write("Upload an agreement and let AI detect harmful clauses.")

# -----------------------------
# LOAD AI MODEL (CACHE)
# -----------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# -----------------------------
# RISK KNOWLEDGE
# -----------------------------
RISK_EXAMPLES = {
    "Termination without notice": [
        "The company may terminate this agreement at any time",
        "The employer can end the contract without prior notice"
    ],
    "Unlimited liability": [
        "You agree to indemnify the company",
        "You are responsible for all losses"
    ],
    "Data misuse": [
        "Your personal data may be shared with third parties",
        "We may distribute your information"
    ],
    "No legal recourse": [
        "You waive your right to sue",
        "Disputes shall be resolved by arbitration only"
    ]
}

RISK_EXPLANATIONS = {
    "Termination without notice":
        "You could suddenly lose your job or contract without warning.",
    "Unlimited liability":
        "You may be forced to pay damages even if you were not fully at fault.",
    "Data misuse":
        "Your personal or sensitive data could be shared or sold.",
    "No legal recourse":
        "You may lose the right to approach a court."
}

# -----------------------------
# PRE-COMPUTE RISK EMBEDDINGS
# -----------------------------
risk_embeddings = {}
for risk, examples in RISK_EXAMPLES.items():
    emb = model.encode(examples, convert_to_tensor=True)
    risk_embeddings[risk] = emb.mean(dim=0)

# -----------------------------
# OCR FUNCTION
# -----------------------------
def extract_text(file):
    if file.type == "application/pdf":
        pages = convert_from_bytes(file.read())
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page)
        return text

    elif file.type.startswith("image"):
        image = Image.open(file)
        return pytesseract.image_to_string(image)

    else:
        return file.read().decode("utf-8")

# -----------------------------
# CLAUSE SPLITTER
# -----------------------------
def split_clauses(text):
    clauses = text.split(".")
    return [c.strip() for c in clauses if len(c.strip()) > 40]

# -----------------------------
# AI RISK DETECTION
# -----------------------------
def detect_risks(clause, threshold=0.6):
    clause_emb = model.encode(clause, convert_to_tensor=True)
    results = []

    for risk, emb in risk_embeddings.items():
        score = util.cos_sim(clause_emb, emb).item()
        if score >= threshold:
            results.append((risk, round(score, 2)))

    return results

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Agreement (PDF / Image / Text)",
    type=["pdf", "png", "jpg", "jpeg", "txt"]
)

if uploaded_file:
    with st.spinner("🔍 Analyzing agreement using AI..."):
        text = extract_text(uploaded_file)
        clauses = split_clauses(text)

    st.success(f"Analysis complete. {len(clauses)} clauses found.")

    found_any = False

    for clause in clauses:
        risks = detect_risks(clause)
        for risk, score in risks:
            found_any = True
            st.warning(f"⚠ {risk} (Confidence: {score})")
            st.write("**Clause:**")
            st.write(clause)
            st.write("**How this can harm you:**")
            st.info(RISK_EXPLANATIONS[risk])

    if not found_any:
        st.success("✅ No major risks detected.")

# -----------------------------
# DISCLAIMER
# -----------------------------
st.markdown("---")
st.caption("⚠ This tool provides informational insights only and does NOT replace legal advice.")
