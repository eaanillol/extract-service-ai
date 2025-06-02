# Extractor de Entidades de Documentos

Este proyecto integra dos APIs:
1. **API de OCR**: Extrae texto de documentos usando Amazon Textract
2. **API de NER**: Extrae entidades del texto usando OpenAI

Además, incluye una interfaz web con Streamlit para facilitar el uso.

## Estructura del Proyecto

```
.
├── api_ocr.py                # API de OCR con Amazon Textract
├── ner-api/                  # API de NER con OpenAI
│   ├── app.py
│   ├── dockerfile
│   └── requirements.txt
├── streamlit_app/            # Interfaz de usuario con Streamlit
│   ├── app.py
│   └── requirements.txt
├── docker-compose.yml        # Configuración de Docker Compose
├── Dockerfile_ocr            # Dockerfile para la API de OCR
├── Dockerfile_streamlit      # Dockerfile para la app de Streamlit
├── requirements.txt          # Requisitos unificados
└── .env.example              # Ejemplo de variables de entorno
```

## Requisitos

- Docker y Docker Compose
- Credenciales de AWS para Amazon Textract
- API Key de OpenAI

## Configuración

1. Copia el archivo `.env.example` a `.env` y completa las variables:

```bash
cp .env.example .env
```

2. Edita el archivo `.env` con tus credenciales:

```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
OPENAI_API_KEY=your_openai_api_key
```

## Ejecución

### Con Docker Compose

```bash
docker-compose up -d
```

Esto iniciará tres servicios:
- API de OCR: http://localhost:5000
- API de NER: http://localhost:8000
- Interfaz Streamlit: http://localhost:8501

### Desarrollo Local

1. Instala las dependencias:

```bash
pip install -r requirements.txt
```

2. Inicia cada servicio por separado:

```bash
# API de OCR
uvicorn api_ocr:app --host 0.0.0.0 --port 5000 --reload

# API de NER
cd ner-api
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Streamlit
cd streamlit_app
streamlit run app.py
```

## Uso

1. Abre la interfaz de Streamlit en http://localhost:8501
2. Sube un documento (PDF, JPG, PNG)
3. Haz clic en "Procesar Documento"
4. Visualiza el texto extraído y las entidades identificadas

## APIs

### API de OCR

- **Endpoint**: `/extract`
- **Método**: POST
- **Cuerpo**: `{"file_base64": "base64_encoded_file"}`
- **Respuesta**: `{"rawText": "texto extraído", "status": "success"}`

### API de NER

- **Endpoint**: `/extract`
- **Método**: POST
- **Cuerpo**: `{"text": "texto a analizar"}`
- **Respuesta**: `{"entities": {"entidad1": "valor1", ...}}`