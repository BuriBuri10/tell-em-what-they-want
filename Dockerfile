FROM python:3.11-slim

# Set working directory to inside your app
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project into the container
COPY . .

# COPY .env .env

# Expose port
EXPOSE 5000

# Run Flask app from correct location
CMD ["python", "flask_app/app.py"]




# FROM python:3.11-slim

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8000

# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]