FROM python:3.11-slim

WORKDIR /app

# Install system-level dependencies for Alpine
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libx11-dev \
    libgl1-mesa-dev \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libpng-dev \
    libharfbuzz-dev \
    libmuparser-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
