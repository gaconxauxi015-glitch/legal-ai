
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pandas as pd
import os

# =========================
# API KEY SAFE SETUP
# =========================
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Thiếu GEMINI_API_KEY. Hãy thêm vào Streamlit Secrets hoặc Environment Variables.")
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# UI
# =========================
st.set_page_config(page_title="Legal AI Assistant")

st.title("⚖️ Legal AI Assistant")
st.write("Trợ lý AI phân tích hợp đồng & pháp lý")

uploaded_file = st.file_uploader(
    "Upload file",
    type=["pdf", "docx", "png", "jpg", "jpeg", "txt", "xlsx"]
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

        # IMAGE
        elif file_name.endswith((".png", ".jpg", ".jpeg")):
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Ảnh đã tải lên")

            img_result = model.generate_content([
                "Đọc nội dung trong ảnh. Nếu là hợp đồng thì phân tích sơ bộ.",
                image
            ])

            document_text = img_result.text

        st.success("✔ Đọc file thành công")

    except Exception as e:
        st.error(f"❌ Lỗi đọc file: {e}")

# =========================
# USER INPUT
# =========================
user_input = st.text_area("Nhập yêu cầu pháp lý")

# =========================
# ANALYZE
# =========================
if st.button("Phân tích"):

    if not document_text:
        st.warning("Không có nội dung file")
        st.stop()

    if not user_input:
        st.warning("Vui lòng nhập yêu cầu")
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
- trả lời rõ ràng, dễ hiểu
"""

    with st.spinner("AI đang phân tích..."):

        try:
            response = model.generate_content(prompt)
            st.subheader("Kết quả phân tích")
            st.write(response.text)

        except Exception as e:
            st.error(f"Lỗi AI: {e}")
