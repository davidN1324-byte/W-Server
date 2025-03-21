FROM python:3.13-slim

# Set up working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt

# Open port that FastAPI uses
EXPOSE 5000

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
#"--ssl-keyfile", "Cert/key.pem", "--ssl-certfile", "Cert/cert.pem"]