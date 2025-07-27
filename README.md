# Maya - AI Content Optimization for Social Platforms

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

Maya is an advanced AI-powered system for optimizing content across social media platforms. It leverages machine learning to analyze, enhance, and schedule content for maximum engagement across Twitter, Instagram, TikTok, and other platforms.

## 🚀 Features

- **AI-Powered Content Analysis**: Sentiment analysis, engagement prediction, and content optimization using OpenAI and HuggingFace models
- **Multi-Platform Support**: Native integrations with Twitter, Instagram, TikTok, Facebook, and LinkedIn
- **Content Processing Pipeline**: Automated content optimization with platform-specific formatting and validation
- **Intelligent Scheduling**: AI-driven optimal posting time recommendations
- **Real-time Monitoring**: Comprehensive metrics, logging, and health monitoring with Prometheus and Grafana
- **Security First**: JWT authentication, input validation, rate limiting, and comprehensive security headers
- **Scalable Architecture**: Containerized microservices with Docker and container orchestration support
- **Developer Friendly**: RESTful API, comprehensive CLI, and extensive documentation

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [CLI Usage](#-cli-usage)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Monitoring](#-monitoring)
- [Contributing](#-contributing)

## 🛠 Installation

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 12+ (for data persistence)
- Redis 6+ (for caching and task queues)

### Option 1: Local Development Installation

```bash
# Clone the repository
git clone https://github.com/stusseligmini/maya.git
cd maya

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Option 2: Docker Installation

```bash
# Clone the repository
git clone https://github.com/stusseligmini/maya.git
cd maya

# Start services with Docker Compose
docker-compose up -d

# For development with hot-reload
docker-compose -f docker-compose.dev.yml up -d
```

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Application Settings
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key-at-least-32-characters-long

# Database Configuration
DATABASE_URL=postgresql://maya:maya@localhost:5432/maya

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# AI Model Configuration
OPENAI_API_KEY=your-openai-api-key
HUGGINGFACE_TOKEN=your-huggingface-token

# Social Platform APIs
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
INSTAGRAM_ACCESS_TOKEN=your-instagram-access-token

# Monitoring
SENTRY_DSN=your-sentry-dsn-optional
LOG_LEVEL=INFO
JSON_LOGS=true
```

## 🚀 Quick Start

### 1. Start the API Server

```bash
# Using Python directly
python -m maya.api.app

# Using the CLI
maya server start --host 0.0.0.0 --port 8000

# Using Docker
docker-compose up maya-api
```

### 2. Create an Authentication Token

```bash
# Using the CLI
maya auth create-token --username demo --email demo@example.com

# Using curl
curl -X POST "http://localhost:8000/auth/token" \
  -d "username=demo&password=demo123"
```

### 3. Process Content

```bash
# Using the CLI
maya content process --text "Check out this amazing AI tool! #AI #Tech" \
  --platforms twitter instagram

# Using the API
curl -X POST "http://localhost:8000/content/process" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "text=Check out this amazing AI tool! #AI #Tech" \
  -d "target_platforms=twitter" \
  -d "target_platforms=instagram"
```

### 4. Publish Content

```bash
# Using the CLI
maya content publish --text "Optimized content for social media!" \
  --platforms twitter instagram

# Schedule for later
maya content schedule --text "Future post content" \
  --platforms twitter --when "2024-12-31 10:00"
```

## 🏗 Architecture

Maya follows a modern microservices architecture designed for scalability and maintainability:

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

# Publish content
POST /content/publish
{
  "content_id": "unique-id",
  "text": "Optimized content",
  "platforms": ["twitter"]
}

# Schedule content
POST /content/schedule
{
  "content_id": "unique-id",
  "text": "Future content",
  "platforms": ["twitter"],
  "publish_time": "2024-12-31T10:00:00Z"
}
```

### AI Operations

```bash
# List available AI models
GET /ai/models

# Analyze content with AI
POST /ai/analyze
{
  "text": "Content to analyze",
  "model_type": "huggingface"
}

# Generate content with AI
POST /ai/generate
{
  "prompt": "Write a social media post about...",
  "model_type": "openai",
  "max_tokens": 150
}
```

### Interactive API Documentation

When running the server, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 💻 CLI Usage

Maya provides a comprehensive command-line interface for all operations:

### Content Operations

```bash
# Process content
maya content process --text "Your content" --platforms twitter instagram

# Publish content
maya content publish --text "Ready to publish" --platforms twitter

# Schedule content
maya content schedule --text "Future post" --platforms twitter --when "2024-12-31 10:00"
```

### AI Operations

```bash
# List AI models
maya ai models

# Analyze content
maya ai analyze --text "Content to analyze" --model huggingface

# Generate content
maya ai generate --prompt "Write about AI" --model openai
```

### Server Management

```bash
# Start server
maya server start --host 0.0.0.0 --port 8000 --reload

# Check system health
maya health
```

### Authentication

```bash
# Create access token
maya auth create-token --username demo --email demo@example.com

# Generate secure password
maya auth generate-password --length 16
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/stusseligmini/maya.git
cd maya

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Start development services
docker-compose -f docker-compose.dev.yml up -d
```

### Code Quality

```bash
# Format code
black maya/ tests/

# Lint code
flake8 maya/ tests/

# Type checking
mypy maya/

# Run all quality checks
pre-commit run --all-files
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🧪 Testing

Maya includes comprehensive test suites for unit, integration, and end-to-end testing.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=maya --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests

# Run tests with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_content"
```

### Test Configuration

Tests use pytest with the following plugins:
- `pytest-asyncio` for async test support
- `pytest-cov` for coverage reporting
- `pytest-mock` for mocking

## 🚀 Deployment

### Production Deployment with Docker

```bash
# Build production image
docker build -t maya:latest .

# Deploy with Docker Compose
docker-compose -f docker-compose.yml up -d

# Scale services
docker-compose up -d --scale maya-api=3
```

### Environment-Specific Configurations

```bash
# Production
cp .env.production .env

# Staging
cp .env.staging .env

# Development
cp .env.development .env
```

### Health Checks and Monitoring

```bash
# Check application health
curl http://localhost:8000/health

# View metrics
curl http://localhost:8000/metrics

# Access Grafana dashboards
open http://localhost:3000
```

## 📊 Monitoring

Maya includes comprehensive monitoring and observability features:

### Metrics Collection

- **Prometheus**: Custom application metrics
- **Grafana**: Visualization dashboards
- **Health checks**: Component status monitoring
- **Performance tracking**: Response time and throughput metrics

### Key Metrics

- HTTP request rates and response times
- AI model usage and performance
- Content processing throughput
- Social platform API rates and errors
- System resource utilization

### Alerting

Configure alerts in `maya/monitoring/metrics.py`:

```python
# Add custom alert rules
alert_manager.add_alert_rule(
    name="high_error_rate",
    condition=lambda metrics: metrics.get("error_rate", 0) > 0.05,
    severity="critical",
    description="Error rate exceeded 5%"
)
```

### Logs

- **Structured logging**: JSON format for production
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Sentry integration**: Error tracking and alerting
- **Request tracing**: Correlation IDs for debugging

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Add docstrings for all public functions
- Update documentation for new features
- Ensure type hints are included

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full documentation](https://maya-docs.example.com)
- **Issues**: [GitHub Issues](https://github.com/stusseligmini/maya/issues)
- **Discussions**: [GitHub Discussions](https://github.com/stusseligmini/maya/discussions)
- **Email**: support@maya-ai.com

## 🔮 Roadmap

- [ ] Advanced content scheduling with ML-driven timing optimization
- [ ] Image and video content processing
- [ ] Additional social platform integrations (LinkedIn, TikTok, YouTube)
- [ ] A/B testing framework for content optimization
- [ ] Real-time engagement analytics and insights
- [ ] Multi-language content support
- [ ] Advanced AI model fine-tuning capabilities
- [ ] Webhook support for external integrations

---

**Made with ❤️ by the Maya Team**
