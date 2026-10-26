FROM python:3.11-slim

WORKDIR /app

# Install system utilities and upgrade pip to avoid installation warnings
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .

# CRITICAL FIX: Explicitly uninstall any modern NumPy variants and force-install legacy 1.x binaries
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y numpy \
    && pip install --no-cache-dir "numpy<2.0.0"

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
