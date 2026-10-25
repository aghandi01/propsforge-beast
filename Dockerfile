FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && python3 -m pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
