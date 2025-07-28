# 🚀 Maya AI Development Setup

## Quick Start Commands

### Development Environment
```bash
# Start core services only
docker-compose up maya-api postgres redis

# Start with background workers
docker-compose up maya-api postgres redis celery-worker celery-beat

# Start with n8n automation
docker-compose up maya-api postgres redis n8n

# Start with monitoring stack
docker-compose --profile monitoring up

# Start production environment
docker-compose --profile production up
```

### Service Access
- **Maya AI API**: http://localhost:8080
- **n8n Automation**: http://localhost:5678 (maya/maya123)
- **Grafana Monitoring**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **PostgreSQL**: localhost:5432 (maya/maya)
- **Redis**: localhost:6379

### Development Profiles

#### Default (Development)
- Maya API
- PostgreSQL
- Redis
- Celery workers

#### With n8n
```bash
docker-compose up maya-api postgres redis n8n
```

#### Production Profile
```bash
docker-compose --profile production up
```
- Includes Nginx reverse proxy
- Production optimized settings

#### Monitoring Profile
```bash
docker-compose --profile monitoring up
```
- Includes Prometheus + Grafana
- Complete metrics collection

### Environment Variables

Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://maya:maya@localhost:5432/maya
REDIS_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_hf_key

# Security
SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256

# n8n
N8N_BASIC_AUTH_USER=maya
N8N_BASIC_AUTH_PASSWORD=maya123
```

### Database Initialization

The PostgreSQL service automatically runs initialization scripts from:
```
database/init/
├── 01_create_tables.sql
├── 02_insert_data.sql
└── 03_create_indexes.sql
```

Ready for development! 🎉
