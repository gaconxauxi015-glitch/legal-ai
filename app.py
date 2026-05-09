
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
import os

# API KEY
import os

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="Legal AI Assistant")

st.title("⚖️ Legal AI Assistant")

st.write("Trợ lý AI pháp lý và hợp đồng")

uploaded_file = st.file_uploader(
    "Upload hợp đồng PDF hoặc Word",
    type=["pdf", "docx"]
)

document_text = ""

if uploaded_file:

    if uploaded_file.name.endswith(".pdf"):

        pdf = PdfReader(uploaded_file)

        for page in pdf.pages:

            text = page.extract_text()

            if text:
                document_text += text

    elif uploaded_file.name.endswith(".docx"):

        doc = Document(uploaded_file)

        for para in doc.paragraphs:
            document_text += para.text + "\n"

    st.success("Đã tải tài liệu")

user_input = st.text_area(
    "Nhập yêu cầu pháp lý"
)

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
    - phân tích rủi ro
    - tìm điều khoản bất lợi
    - đề xuất chỉnh sửa
    - trả lời dễ hiểu
    """

    response = model.generate_content(prompt)

    st.write(response.text)
