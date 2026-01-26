FROM python:3.11-slim

# System deps (needed for Playwright + curl for healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libcairo2 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Install Chromium ONLY because you decided to keep browser scraping
RUN python -m playwright install chromium

COPY . .

# 🔴 THIS IS THE MOST IMPORTANT LINE
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

