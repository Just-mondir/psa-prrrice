# Pokemon Card Price Automation Service

This web service automates the process of fetching Pokemon card prices. It uses Playwright for web automation and provides a simple web interface for users to upload their Google Service Account JSON file and specify the Google Sheet name.

## Features

- Web interface for file upload and automation control
- Headless browser automation using Playwright
- Google Sheets integration for data storage
- Docker containerization for easy deployment
- Railway.app deployment ready

## Deployment on Railway

1. Fork or clone this repository
2. Sign up on [Railway.app](https://railway.app)
3. Create a new project and connect it to your GitHub repository
4. Railway will automatically detect the Dockerfile and deploy your application
5. Add any necessary environment variables in Railway dashboard

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Run the application:
```bash
python app.py
```

## Environment Variables

- `PORT`: Port number (default: 8080)
- `PYTHONUNBUFFERED`: Python output buffering (set to 1)

## Docker

Build locally:
```bash
docker build -t pokemon-price-automation .
docker run -p 8080:8080 pokemon-price-automation
```

## Notes

- Make sure your Google Service Account JSON file has the necessary permissions
- The sheet should follow the expected format for the automation to work correctly
- The service runs in headless mode for better performance