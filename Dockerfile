# Gunakan image Python
FROM python:3.10

# Atur direktori kerja di dalam container
WORKDIR /app

# Copy semua file ke dalam container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan bot
CMD ["python", "main.py"]
