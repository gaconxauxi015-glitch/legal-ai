import streamlit as st
from google import genai
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pandas as pd
import os

# =========================
# API KEY
# =========================
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Missing GEMINI_API_KEY")
    st.stop()

# IMPORTANT: NEW SDK CLIENT
client = genai.Client(api_key=api_key)

# =========================
# UI
# =========================
st.set_page_config(page_title="Legal AI Assistant")

st.title("⚖️ Legal AI Assistant")

uploaded_file = st.file_uploader(
    "Upload file",
    type=["pdf", "docx", "txt", "xlsx", "png", "jpg", "jpeg"]
)

document_text = ""

# =========================
# FILE READER
# =========================
if uploaded_file:

    name = uploaded_file.name.lower()

    try:

        if name.endswith(".pdf"):
            pdf = PdfReader(uploaded_file)
            document_text = "\n".join([p.extract_text() or "" for p in pdf.pages])

        elif name.endswith(".docx"):
            doc = Document(uploaded_file)
            document_text = "\n".join([p.text for p in doc.paragraphs])

        elif name.endswith(".txt"):
            document_text = uploaded_file.read().decode()

        elif name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            document_text = df.to_string()

        elif name.endswith((".png", ".jpg", ".jpeg")):

            image = Image.open(uploaded_file)
            st.image(image)

            res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    image,
                    "Extract and analyze this legal document."
                ]
            )

            document_text = res.text

        st.success("File loaded")

    except Exception as e:
        st.error(f"File error: {e}")

# =========================
# USER INPUT
# =========================
question = st.text_area("Ask legal question")

# =========================
# AI ANALYSIS
# =========================
if st.button("Analyze"):

    if not document_text:
        st.warning("No file content")
        st.stop()

    prompt = f"""
You are a legal expert in Vietnam.

DOCUMENT:
{document_text}

QUESTION:
{question}

Analyze:
- risks
- unfair clauses
- suggestions
- clear explanation
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        st.subheader("Result")
        st.write(response.text)

    except Exception as e:
        st.error(f"AI error: {e}")
        except Exception as e:
            st.error(f"Lỗi AI: {e}")
