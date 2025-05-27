FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .

# Crear directorio temporal para archivos
RUN mkdir -p /tmp

# Exponer el puerto 5000
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000"]
