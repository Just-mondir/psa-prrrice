FROM mcr.microsoft.com/playwright/python:v1.39.0-jammy

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Create upload directory
RUN mkdir -p uploads

# Ensure correct permissions
RUN chmod -R 755 /app

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8080

# Start the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "0", "app:app"]