# Base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Install dependencies first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Expose port (Railway uses $PORT env variable)
EXPOSE 8000

# Start command - Railway will set $PORT automatically
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

