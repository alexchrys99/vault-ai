FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .

# Install, build, and purge in one lightweight step (No PyTorch needed!)
RUN apt-get update -o Acquire::Check-Valid-Until=false \
    && apt-get install -y build-essential sqlite3 \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip

COPY . .
