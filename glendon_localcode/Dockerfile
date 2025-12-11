# Use Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app


# Install system dependencies (needed for some database tools)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code (controllers, logics, main.py, etc.)
COPY . .

# Expose the port
EXPOSE 8000

# START THE APP
# "main:app" means: Go to main.py and look for the variable 'app'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]