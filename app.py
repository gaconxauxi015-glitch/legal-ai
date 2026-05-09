
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pandas as pd
import os

# =========================
# API KEY SETUP
# =========================
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Chưa set GEMINI_API_KEY trong environment variables")
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# UI
# =========================
st.set_page_config(page_title="Legal AI Assistant")

st.title("⚖️ Legal AI Assistant")
st.write("Trợ lý AI pháp lý và hợp đồng")

uploaded_file = st.file_uploader(
    "Upload hợp đồng PDF / Word / Image / Excel / Text",
    type=["pdf", "docx", "png", "jpg", "jpeg", "txt", "xlsx"]
)

document_text = ""

# =========================
# FILE PROCESSING
# =========================
if uploaded_file:

    file_name = uploaded_file.name.lower()

    # PDF
    if file_name.endswith(".pdf"):
        pdf = PdfReader(uploaded_file)
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                document_text += text

    # DOCX
    elif file_name.endswith(".docx"):
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            document_text += para.text + "\n"

    # TXT
    elif file_name.endswith(".txt"):
        document_text = uploaded_file.read().decode("utf-8")

    # EXCEL
    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        document_text = df.to_string()

    # IMAGE (IMPORTANT FIX)
    elif file_name.endswith((".png", ".jpg", ".jpeg")):
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh đã tải lên")

        try:
            response = model.generate_content([
                "Hãy đọc toàn bộ nội dung trong ảnh này. Nếu là hợp đồng thì phân tích sơ bộ.",
                image.convert("RGB")
            ])

            document_text = response.text

        except Exception as e:
            st.error(f"Lỗi xử lý ảnh: {e}")
            document_text = ""

    st.success("Đã tải tài liệu")

# =========================
# USER INPUT
# =========================
user_input = st.text_area("Nhập yêu cầu pháp lý")

# =========================
# ANALYZE BUTTON
# =========================
if st.button("Phân tích"):

    if not user_input:
        st.warning("Vui lòng nhập yêu cầu")
        st.stop()

    if not document_text:
        st.warning("Không đọc được nội dung file")
        st.stop()

    prompt = f"""
Bạn là chuyên gia pháp lý lao động tại Việt Nam.

Tài liệu:
{document_text}

Yêu cầu:
{user_input}

Hãy:
- phân tích rủi ro pháp lý
- tìm điều khoản bất lợi
- đề xuất chỉnh sửa
- trả lời dễ hiểu
- trình bày rõ ràng theo từng mục
"""

    with st.spinner("AI đang phân tích..."):
        response = model.generate_content(prompt)

    st.subheader("Kết quả phân tích")
    st.write(response.text)
