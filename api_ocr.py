from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import boto3
import os
import base64
import logging
import uvicorn
import dotenv
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno si existe el archivo .env
try:
    dotenv.load_dotenv()
except:
    logger.info("No se encontró archivo .env, usando variables de entorno del sistema")

app = FastAPI(title="Textract API", description="API para extraer texto de documentos PDF usando Amazon Textract")

# Modelo para la solicitud
class DocumentRequest(BaseModel):
    file_base64: str

@app.post("/extract", summary="Extraer texto de un documento PDF")
async def extract_text(request: DocumentRequest):
    """
    Extrae texto de un documento PDF usando Amazon Textract.
    
    - **file_base64**: Archivo PDF codificado en base64
    
    Retorna el texto extraído del documento.
    """
    try:
        # Decodificar el archivo base64
        try:
            file_bytes = base64.b64decode(request.file_base64)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error al decodificar el archivo base64: {str(e)}"
            )
        
        # Configurar cliente de Textract con credenciales
        textract = boto3.client(
            'textract',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN')
        )
        
        # Llamar a Textract para detectar texto
        response = textract.detect_document_text(Document={'Bytes': file_bytes})
        
        # Extraer el texto
        raw_text = ""
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                raw_text += item['Text'] + "\n"
        
        # Devolver el texto extraído
        return {"rawText": raw_text, "status": "success"}
    
    except Exception as e:
        logger.error(f"Error al procesar el archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api_ocr:app", host="0.0.0.0", port=5000, reload=True)