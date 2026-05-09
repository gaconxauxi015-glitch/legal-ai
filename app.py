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
    st.error("❌ Missing GEMINI_API_KEY")
    st.stop()

# =========================
# CALL GEMINI (REST)
# =========================
def call_gemini(prompt, image=None):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    parts = [{"text": prompt}]

    # nếu có ảnh
    if image:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_b64 = base64.b64encode(buffer.getvalue()).decode()

        parts.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": img_b64
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
st.title("⚖️ Legal AI (REST API VERSION)")
st.write("Bản không SDK – không lỗi 404")

file = st.file_uploader(
    "Upload file",
    type=["pdf", "docx", "txt", "xlsx", "png", "jpg", "jpeg"]
)

text = ""
image_obj = None

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

    elif name.endswith((".png", ".jpg", ".jpeg")):
        image_obj = Image.open(file)
        st.image(image_obj)

    st.success("File loaded")

# =========================
# INPUT
# =========================
question = st.text_area("Nhập yêu cầu pháp lý")

# =========================
# ANALYZE
# =========================
if st.button("Phân tích"):

    if not text and not image_obj:
        st.warning("Chưa có file")
        st.stop()

    prompt = f"""
Bạn là luật sư Việt Nam.

Tài liệu:
{text}

Yêu cầu:
{question}

Hãy:
- phân tích rủi ro pháp lý
- chỉ ra điều khoản bất lợi
- đề xuất chỉnh sửa
- trả lời dễ hiểu
"""

    with st.spinner("AI đang xử lý..."):

        result = call_gemini(prompt, image_obj)

        try:
            output = result["candidates"][0]["content"]["parts"][0]["text"]

            st.subheader("Kết quả")
            st.write(output)

        except Exception:
            st.error("Lỗi API")
            st.json(result)
        st.error(result)
