# Maya - AI Content Optimization for Social Platforms

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)


```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │  Load Balancer  │    │     Nginx       │
│   (FastAPI)     │    │     (Nginx)     │    │   (Reverse      │
│                 │    │                 │    │    Proxy)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Content        │    │   AI Models     │    │   Social        │
│  Processor      │    │   Integration   │    │   Platforms     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │     Redis       │    │   Monitoring    │
│  (PostgreSQL)   │    │   (Cache &      │    │  (Prometheus/   │
│                 │    │   Queue)        │    │   Grafana)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

#### 1. **API Layer** (`maya.api`)
- FastAPI-based REST API
- JWT authentication and authorization
- Rate limiting and security middleware
- Comprehensive error handling

#### 2. **Content Processing** (`maya.content`)
- Platform-specific content optimization
- Content validation and formatting
- Hashtag and mention processing
- Multi-platform content adaptation

#### 3. **AI Integration** (`maya.ai`)
- OpenAI GPT models for content generation and analysis
- HuggingFace transformers for sentiment analysis
- Configurable model selection and fallbacks
- Content enhancement recommendations

#### 4. **Social Platform Integration** (`maya.social`)
- Twitter/X API integration
- Instagram Business API integration
- Scheduling and publishing workflow
- Content unpublishing and management

#### 5. **Security** (`maya.security`)
- JWT token management
- Password hashing and validation
- Input sanitization and validation
- Rate limiting and security headers

#### 6. **Monitoring** (`maya.monitoring`)
- Prometheus metrics collection
- Health checks and alerting
- Performance tracking
- Structured logging with Sentry integration

## ⚙️ Configuration

Maya uses Pydantic Settings for configuration management with support for environment variables and configuration files.

### Database Settings

```python
DATABASE_URL=postgresql://user:password@host:port/database
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### AI Model Configuration

```python
OPENAI_API_KEY=sk-...
HUGGINGFACE_TOKEN=hf_...
MODEL_CACHE_DIR=./models/cache
```

### Security Configuration

```python
SECRET_KEY=your-secret-key-32-chars-minimum
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_HOSTS=["*"]  # Restrict in production
```

## 📚 API Documentation

### Authentication

All API endpoints require JWT authentication except for health checks and token creation.

```bash
# Get access token
POST /auth/token
{
  "username": "demo",
  "password": "demo123"
}

# Use token in requests
Authorization: Bearer <token>
```

### Content Processing

```bash
# Process content for optimization
POST /content/process
{
  "text": "Your content here",
  "content_type": "text",
  "target_platforms": ["twitter", "instagram"],
  "analyze_with_ai": true
}
