# Use a specific Python Alpine version
#FROM python:3.9.18-alpine3.18
FROM python:3.12-slim-bookworm
# Add labels for better maintainability
LABEL maintainer="devraj21"
LABEL description="Streamlit reconciliation application with file upload capabilities"

# Install system dependencies
# RUN apk update && apk add --no-cache \
#     curl \
#     gcc \
#     musl-dev \
#     linux-headers \
#     build-base \
#     libffi-dev \
#     openssl-dev \
#     python3-dev \
#     py3-numpy \
#     py3-pandas \
#     && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/logs /app/outputs && \
    chmod -R 777 /app/logs /app/outputs

# Copy requirements first (better caching)
COPY app/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
     && pip3 install -r requirements.txt

# Copy the application code
COPY app/ .

# Expose port 8501 (Streamlit's default port)
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Set the command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]