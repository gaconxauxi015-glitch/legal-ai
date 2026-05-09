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
    st.error("❌ Thiếu GEMINI_API_KEY")
    st.stop()

# =========================
# GEMINI CALL (FIX TRIỆT ĐỂ - V1 API)
# =========================
def call_gemini(prompt, image=None):

    # ⚠️ QUAN TRỌNG: dùng v1 (KHÔNG v1beta)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    parts = [{"text": prompt}]

    # xử lý ảnh nếu có
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

    response = requests.post(url, json=payload)
    return response.json()

# =========================
# UI
# =========================
st.set_page_config(page_title="Legal AI")

st.title("⚖️ Legal AI (FINAL STABLE VERSION)")
st.write("Không SDK – không v1beta – không lỗi 404")

uploaded_file = st.file_uploader(
    "Upload file",
    type=["pdf", "docx", "txt", "xlsx", "png", "jpg", "jpeg"]
)

text_data = ""
image_data = None

# =========================
# READ FILE
# =========================
if uploaded_file:

    name = uploaded_file.name.lower()

    try:
        # PDF
        if name.endswith(".pdf"):
            pdf = PdfReader(uploaded_file)
            text_data = "\n".join([p.extract_text() or "" for p in pdf.pages])

        # DOCX
        elif name.endswith(".docx"):
            doc = Document(uploaded_file)
            text_data = "\n".join([p.text for p in doc.paragraphs])

        # TXT
        elif name.endswith(".txt"):
            text_data = uploaded_file.read().decode()

        # XLSX
        elif name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            text_data = df.to_string()

        # IMAGE
        elif name.endswith((".png", ".jpg", ".jpeg")):
            image_data = Image.open(uploaded_file)
            st.image(image_data, caption="Uploaded Image")

        st.success("✔ File loaded")

    except Exception as e:
        st.error(f"File error: {e}")

# =========================
# INPUT
# =========================
question = st.text_area("Nhập yêu cầu pháp lý")

# =========================
# ANALYZE
# =========================
if st.button("Phân tích"):

    if not text_data and not image_data:
        st.warning("Chưa có file")
        st.stop()

    prompt = f"""
Bạn là luật sư Việt Nam.

Tài liệu:
{text_data}

Yêu cầu:
{question}

Hãy:
- phân tích rủi ro pháp lý
- chỉ ra điều khoản bất lợi
- đề xuất chỉnh sửa
- trình bày rõ ràng dễ hiểu
"""

    with st.spinner("AI đang phân tích..."):

        result = call_gemini(prompt, image_data)

        try:
            output = result["candidates"][0]["content"]["parts"][0]["text"]

            st.subheader("Kết quả")
            st.write(output)

        except Exception:
            st.error("Lỗi API:")
            st.json(result)
