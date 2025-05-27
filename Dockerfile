FROM python:3.9

WORKDIR /app

COPY requirements_ocr.txt .
RUN pip install --no-cache-dir -r requirements_ocr.txt

COPY api_ocr.py .

# Crear directorio temporal para archivos
RUN mkdir -p /tmp

# Exponer el puerto 5000
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "-m", "uvicorn", "api_ocr:app", "--host", "0.0.0.0", "--port", "5000"]
