FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY backend/ .

# Expose and run
ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


