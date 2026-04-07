FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for HF Space
EXPOSE 7860

# Default: run the FastAPI server for HF Space
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]