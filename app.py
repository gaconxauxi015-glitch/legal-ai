import streamlit as st
import requests
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pandas as pd
import base64
import io
import os

# =========================
# API KEY
# =========================
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("Thiếu GEMINI_API_KEY")
    st.stop()

# =========================
# CALL GEMINI (REST API - ỔN ĐỊNH)
# =========================
def ask_gemini(prompt, image=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    parts = [{"text": prompt}]

    if image:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        parts.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": img_base64
            }
        })

    payload = {
        "contents": [
            {
                "parts": parts
            }
        ]
    }

    res = requests.post(url, json=payload)
    return res.json()

# =========================
# UI
# =========================
st.title("⚖️ Legal AI (Stable Version)")
st.write("Không lỗi SDK - chạy ổn định")

file = st.file_uploader("Upload file", type=["pdf","docx","txt","xlsx","png","jpg","jpeg"])

text = ""

# =========================
# READ FILE
# =========================
if file:

    name = file.name.lower()

    if name.endswith(".pdf"):
        pdf = PdfReader(file)
        text = "\n".join([p.extract_text() or "" for p in pdf.pages])

    elif name.endswith(".docx"):
        doc = Document(file)
        text = "\n".join([p.text for p in doc.paragraphs])

    elif name.endswith(".txt"):
        text = file.read().decode()

    elif name.endswith(".xlsx"):
        df = pd.read_excel(file)
        text = df.to_string()

    elif name.endswith((".png","jpg","jpeg")):
        image = Image.open(file)
        st.image(image)

        st.session_state.image = image

    st.success("Loaded file")

# =========================
# INPUT
# =========================
question = st.text_area("Ask")

# =========================
# ANALYZE
# =========================
if st.button("Analyze"):

    prompt = f"""
Bạn là luật sư Việt Nam.

Tài liệu:
{text}

Câu hỏi:
{question}

Hãy phân tích rõ rủi ro và đề xuất.
"""

    if hasattr(st.session_state, "image"):
        result = ask_gemini(prompt, st.session_state.image)
    else:
        result = ask_gemini(prompt)

    try:
        st.subheader("Kết quả")
        st.write(result["candidates"][0]["content"]["parts"][0]["text"])
    except:
        st.error(result)
