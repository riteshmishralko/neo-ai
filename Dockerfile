FROM python:3.12-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt upgrade -y

RUN apt-get install -y --no-install-recommends \
    portaudio19-dev \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set workdir before copying files
WORKDIR /neo-ai

# Copy requirements first for better caching and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN huggingface-cli login --token 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


# Copy the rest of the application code
COPY . .

# (Optional) If you need to copy environment variables from environment.list:
# COPY environment.list .env

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Start the FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--forwarded-allow-ips", "*", "--workers", "1"]