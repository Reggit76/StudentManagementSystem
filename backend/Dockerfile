# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make scripts directory executable
RUN chmod +x scripts/*

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Waiting for database..."\n\
sleep 10\n\
echo "Initializing system..."\n\
python scripts/init_system.py\n\
echo "Starting application..."\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]