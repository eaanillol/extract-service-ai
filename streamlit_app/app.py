import streamlit as st
import requests
import json
import base64
import os
import pandas as pd
from PIL import Image
from io import BytesIO

# URLs de las APIs (configuradas en docker-compose)
OCR_API_URL = os.getenv("OCR_API_URL", "http://textract-api:5000")
NER_API_URL = os.getenv("NER_API_URL", "http://ner-api:8000")

st.set_page_config(
    page_title="Extractor de Entidades de Documentos",
    page_icon="📄",
    layout="wide"
)

def extract_text_from_document(file_bytes):
    """Envía el documento al API de OCR y obtiene el texto extraído"""
    try:
        # Codificar el archivo en base64
        file_base64 = base64.b64encode(file_bytes).decode('utf-8')
        
        # Enviar al API de OCR
        response = requests.post(
            f"{OCR_API_URL}/extract",
            json={"file_base64": file_base64},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("rawText", "")
        else:
            st.error(f"Error en la extracción de texto: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error al procesar el documento: {str(e)}")
        return None

def extract_entities(text):
    """Envía el texto al API de NER y obtiene las entidades extraídas"""
    try:
        response = requests.post(
            f"{NER_API_URL}/extract",
            json={"text": text},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("entities", {})
        else:
            st.error(f"Error en la extracción de entidades: {response.text}")
            return {}
    except Exception as e:
        st.error(f"Error al extraer entidades: {str(e)}")
        return {}

def display_entities(entities):
    """Muestra las entidades extraídas en una tabla"""
    if not entities:
        st.warning("No se encontraron entidades en el documento.")
        return
    
    # Convertir el diccionario de entidades a un DataFrame
    df = pd.DataFrame(list(entities.items()), columns=["Entidad", "Valor"])
    
    # Mostrar el DataFrame como una tabla
    st.subheader("Entidades Extraídas")
    st.table(df)

def main():
    st.title("📄 Extractor de Entidades de Documentos")
    st.write("Sube un documento para extraer texto y entidades.")
    
    # Columnas para la interfaz
    col1, col2 = st.columns([1, 1])
    
    # Subida de archivos
    uploaded_file = st.file_uploader("Elige un documento (PDF, JPG, PNG)", 
                                    type=["pdf", "jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Mostrar información del archivo
        file_details = {
            "Nombre": uploaded_file.name,
            "Tipo": uploaded_file.type,
            "Tamaño": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.write("Detalles del archivo:")
        st.json(file_details)
        
        # Leer el archivo
        file_bytes = uploaded_file.read()
        
        # Si es una imagen, mostrarla
        if uploaded_file.type.startswith('image'):
            with col1:
                st.subheader("Documento Original")
                st.image(Image.open(BytesIO(file_bytes)), use_column_width=True)
        
        # Botón para procesar
        if st.button("Procesar Documento"):
            with st.spinner("Extrayendo texto del documento..."):
                # Extraer texto
                extracted_text = extract_text_from_document(file_bytes)
                
                if extracted_text:
                    with col1:
                        st.subheader("Texto Extraído")
                        st.text_area("", extracted_text, height=400)
                    
                    with st.spinner("Extrayendo entidades..."):
                        # Extraer entidades
                        entities = extract_entities(extracted_text)
                        
                        with col2:
                            display_entities(entities)
                            
                            # Mostrar JSON de entidades
                            st.subheader("JSON de Entidades")
                            st.json(entities)

if __name__ == "__main__":
    main()