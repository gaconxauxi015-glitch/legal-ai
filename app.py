
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
    st.error("❌ Thiếu GEMINI_API_KEY trong Streamlit Secrets hoặc Environment Variables")
    st.stop()

client = genai.Client(api_key=api_key)

# =========================
# UI
# =========================
st.set_page_config(page_title="Legal AI Assistant")

st.title("⚖️ Legal AI Assistant")
st.write("Phân tích hợp đồng & tài liệu pháp lý bằng AI")

uploaded_file = st.file_uploader(
    "Upload file (PDF / DOCX / TXT / XLSX / IMAGE)",
    type=["pdf", "docx", "txt", "xlsx", "png", "jpg", "jpeg"]
)

document_text = ""

# =========================
# READ FILE
# =========================
if uploaded_file:

    file_name = uploaded_file.name.lower()

    try:

        # PDF
        if file_name.endswith(".pdf"):
            pdf = PdfReader(uploaded_file)
            document_text = "\n".join([p.extract_text() or "" for p in pdf.pages])

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

        # IMAGE (FIX CHUẨN GEMINI SDK MỚI)
        elif file_name.endswith((".png", ".jpg", ".jpeg")):

            image = Image.open(uploaded_file)
            st.image(image, caption="Ảnh đã tải lên")

            response = client.models.generate_content(
                model="gemini-1.5-flash-001",
                contents=[
                    image,
                    "Đọc nội dung trong ảnh. Nếu là hợp đồng thì phân tích sơ bộ."
                ]
            )

            document_text = response.text

        st.success("✔ Đọc file thành công")

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
            response = client.models.generate_content(
                model="gemini-1.5-flash-001",
                contents=prompt
            )

            st.subheader("Kết quả phân tích")
            st.write(response.text)

        except Exception as e:
            st.error(f"Lỗi AI: {e}")
