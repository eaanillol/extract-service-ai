# main.py
import json
import logging
import os
from typing import Any, Dict
import dotenv

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from openai import OpenAI            # SDK ≥ 1.30

# -------------------------------------------------------------------------
# Configuración global
# -------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
try:
    dotenv.load_dotenv()
except:
    logger.info("No se encontró archivo .env, usando variables de entorno del sistema")


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Falta la variable de entorno OPENAI_API_KEY")



client = OpenAI(
    api_key=OPENAI_API_KEY
)

MODEL = "gpt-4o-mini"
TEMPERATURE = 0
MAX_TOKENS = 512

# -------------------------------------------------------------------------
# Esquema de entidades
# -------------------------------------------------------------------------
ENTITY_SCHEMA = {
    "employee_name":   "Nombre completo del empleado",
    "employer_name":   "Nombre de la empresa que emite la carta",
    "job_title":       "Cargo desempeñado",
    "start_date":      "Fecha de inicio (YYYY-MM-DD preferido)",
    "end_date":        "Fecha de salida (null si sigue activo)",
    "salary":          "Salario (numérico o string, null si no aparece)",
    "salary_currency": "ISO 4217, null si no aplica",
    "reference_name":  "Nombre de quien firma / referencia",
    "reference_role":  "Cargo de quien firma / referencia",
}

SYSTEM_PROMPT = (
    "Eres un analista de RRHH experto en extracción de información. "
    "Devuelve ÚNICAMENTE un JSON válido con las claves y valores definidos "
    "en el esquema anterior, sin comentarios adicionales."
)

# -------------------------------------------------------------------------
# Modelos Pydantic
# -------------------------------------------------------------------------
class DocumentIn(BaseModel):
    text: str = Field(..., description="Carta de certificación laboral en texto plano")

class EntitiesOut(BaseModel):
    entities: Dict[str, Any]

# -------------------------------------------------------------------------
# FastAPI
# -------------------------------------------------------------------------
app = FastAPI(
    title="Employment-Certificate NER API",
    version="0.2.0",
    description="Extrae entidades de cartas de certificación laboral usando OpenAI",
)

# -------------------------------------------------------------------------
# Funciones auxiliares
# -------------------------------------------------------------------------
def call_openai(raw_text: str) -> Dict[str, Any]:
    """Envía la carta al modelo y devuelve las entidades como dict."""
    user_prompt = (
        f"Esquema JSON requerido:\n{json.dumps(ENTITY_SCHEMA, ensure_ascii=False)}\n\n"
        f"Carta:\n\"\"\"\n{raw_text}\n\"\"\""
    )

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
        )
        content = resp.choices[0].message.content.strip()
        return json.loads(content)  # valida que sea JSON
    except (json.JSONDecodeError, KeyError) as parse_err:
        logging.exception("El modelo no devolvió JSON válido")
        raise HTTPException(
            status_code=502,
            detail=f"Respuesta no parseable de OpenAI: {parse_err}",
        )
    except Exception as exc:
        logging.exception("Error llamando a OpenAI")
        raise HTTPException(status_code=502, detail=str(exc))

# -------------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------------
@app.get("/ping")
async def ping():
    """Health-check sencillo."""
    return {"status": "ok"}

@app.post("/extract", response_model=EntitiesOut, tags=["NER"])
async def extract_entities(doc: DocumentIn):
    """Extrae entidades a partir de un JSON {"text": "..."}."""
    entities = call_openai(doc.text)
    return {"entities": entities}

@app.post("/extract-text", response_model=EntitiesOut, tags=["NER"])
async def extract_entities_raw(request: Request):
    """
    Variante que acepta texto plano en el body (Content-Type: text/plain
    o application/octet-stream).
    """
    raw_text = (await request.body()).decode()
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="El cuerpo está vacío")
    entities = call_openai(raw_text)
    return {"entities": entities}
