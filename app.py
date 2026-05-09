
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pandas as pd
import os
import io

# =========================
# API KEY SETUP (SAFE)
# =========================
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Thiếu GEMINI_API_KEY (set trong Streamlit Secrets hoặc Environment Variables)")
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-pro")

# =========================
# UI
# =========================
st.set_page_config(page_title="Legal AI Assistant")

st.title("⚖️ Legal AI Assistant")
st.write("Phân tích hợp đồng & tài liệu pháp lý bằng AI")

uploaded_file = st.file_uploader(
    "Upload file",
    type=["pdf", "docx", "png", "jpg", "jpeg", "txt", "xlsx"]
)

document_text = ""

# =========================
# PROCESS FILE
# =========================
if uploaded_file:

    file_name = uploaded_file.name.lower()

    try:

        # PDF
        if file_name.endswith(".pdf"):
            pdf = PdfReader(uploaded_file)
            document_text = "\n".join(
                [page.extract_text() or "" for page in pdf.pages]
            )

        # DOCX
        elif file_name.endswith(".docx"):
            doc = Document(uploaded_file)
            document_text = "\n".join([p.text for p in doc.paragraphs])

        # TXT
        elif file_name.endswith(".txt"):
            document_text = uploaded_file.read().decode("utf-8")

        # EXCEL
        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            document_text = df.to_string()

        # IMAGE (FIX CHUẨN GEMINI)
        elif file_name.endswith((".png", ".jpg", ".jpeg")):

            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Ảnh đã tải lên")

            # convert image → bytes (FIX QUAN TRỌNG)
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="PNG")
            img_bytes = img_bytes.getvalue()

            response = model.generate_content([
                {
                    "mime_type": "image/png",
                    "data": img_bytes
                },
                "Hãy đọc toàn bộ nội dung trong ảnh. Nếu là hợp đồng thì phân tích sơ bộ."
            ])

            document_text = response.text

        st.success("✔ Đã đọc file thành công")

    except Exception as e:
        st.error(f"❌ Lỗi xử lý file: {e}")

# =========================
# USER INPUT
# =========================
user_input = st.text_area("Nhập yêu cầu pháp lý")

# =========================
# ANALYZE
# =========================
if st.button("Phân tích"):

    if not document_text:
        st.warning("❌ Không có nội dung file")
        st.stop()

    if not user_input:
        st.warning("❌ Vui lòng nhập yêu cầu")
        st.stop()

    prompt = f"""
Bạn là chuyên gia pháp lý tại Việt Nam.

Tài liệu:
{document_text}

Yêu cầu:
{user_input}

Hãy:
- phân tích rủi ro pháp lý
- chỉ ra điều khoản bất lợi
- đề xuất chỉnh sửa
- trình bày rõ ràng, dễ hiểu
"""

    with st.spinner("AI đang phân tích..."):

        try:
            result = model.generate_content(prompt)
            st.subheader("Kết quả phân tích")
            st.write(result.text)

        except Exception as e:
            st.error(f"Lỗi AI: {e}")
