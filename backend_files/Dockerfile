FROM python:3.11-slim

WORKDIR /app

# 1. Install critical system utilities and upgrade build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip setuptools wheel

# 2. ISOLATION STEP: Force-install legacy NumPy FIRST before anything else compiles
RUN pip install --no-cache-dir "numpy==1.26.4"

# 3. Bring in the rest of the application package targets
COPY requirements.txt .

# 4. Install remaining packages (pip will respect and align with the existing 1.26.4 NumPy install)
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
