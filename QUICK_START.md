# Maya AI - Quick Start

## Start with Docker (recommended)

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Start all services:
   ```bash
   docker-compose up --build
   ```

3. Access:
   - Maya API: http://localhost:8000
   - n8n Automation: http://localhost:5678 (admin/admin123)
   - API Documentation: http://localhost:8000/docs

## Endpoints

- **Login**: `POST /auth/login` 
- **Generate Content**: `POST /ai/generate`
- **Process Content**: `POST /content/process`
- **n8n Webhook**: `POST /integrations/n8n/webhook`

## For Development

```bash
python maya_run.py api --reload
```

## Deploy to Render

See `RENDER_DEPLOYMENT_GUIDE.md` for production deployment.
