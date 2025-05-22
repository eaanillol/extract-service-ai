import streamlit as st 
from streamlit_pdf_viewer import pdf_viewer
st.title("BCB Document Extraction")






container_pdf, container_results = st.columns([100, 100])
with container_pdf:
    pdf_file = st.file_uploader("Upload PDF file", type=('pdf'))

    if pdf_file:
        binary_data = pdf_file.getvalue()
        pdf_viewer(input=binary_data,
                   width=700)

container_pdf, container_chat = st.columns([50, 50])
with container_results:
    st.write("Results of extraction")