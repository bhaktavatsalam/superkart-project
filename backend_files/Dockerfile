FROM python:3.11-slim

WORKDIR /app

# Ensure container system packages are updated and pip is at the absolute latest version
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .

# Force a clean installation directly from the remote repository mirrors
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
