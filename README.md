# 🚀 Maya AI - Content Optimization System

> AI-powered content creation and social media management platform with mobile PWA support

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/stusseligmini/maya)

## 📖 Overview

Maya AI is an advanced AI-powered content optimization system designed for social media creators and businesses. It combines machine learning, automated content generation, and multi-platform publishing capabilities with a modern Progressive Web App (PWA) interface.

## 🌟 Key Features

### 🤖 AI-Powered Content Creation
- **Image Generation**: Integration with Fooocus and AI models for high-quality visuals
- **Smart Caption Generation**: OpenAI GPT-powered captions optimized for each platform
- **Content Enhancement**: Automatic image optimization and text refinement
- **Hashtag Intelligence**: AI-generated relevant hashtags for maximum reach

### 📱 Progressive Web App (PWA)
- **Mobile Installation**: Install as native app on iOS/Android devices
- **Offline Support**: Content creation works without internet connection
- **Touch Optimized**: Mobile-first responsive design
- **Push Notifications**: Real-time content status updates
- **Cross-Platform**: Works on desktop, tablet, and mobile

### � Multi-Platform Publishing
- **Instagram**: Photos, Stories, Reels with optimal timing
- **TikTok**: Short-form videos with trending hashtags
- **Twitter**: Text and media posts with character optimization
- **Fanvue**: Creator-focused content distribution
- **Snapchat**: Engaging stories and snaps

### 🔍 Content Moderation & Safety
- **AI Safety Scoring**: Automatic content appropriateness detection
- **NSFW Detection**: Advanced filtering for inappropriate content
- **Telegram Review**: Human oversight through bot integration
- **Quality Assurance**: Automated image and text quality checks

### 🔄 Automated Workflow
- **Background Processing**: Celery-powered async task processing
- **Smart Queue Management**: Priority-based content processing
- **Real-time Analytics**: Performance tracking and insights
- **Auto-posting**: Scheduled content distribution

### 💬 Telegram Integration
- **Review Workflow**: Human review via Telegram bot
- **One-click Approval**: Approve/reject content instantly
- **Content Editing**: Edit captions and regenerate content
- **Status Notifications**: Real-time updates and alerts

## 🚀 Quick Start

### 🌐 Deploy to Render (Recommended)

**One-Click Deploy**: 
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/stusseligmini/maya)

**Manual Setup**:
```bash
git clone https://github.com/stusseligmini/maya.git
cd maya
# Follow RENDER_DEPLOYMENT_GUIDE.md for complete setup
```

### 📱 Install Mobile PWA

After deployment, install Maya AI as a mobile app:

**iPhone (iOS):**
1. Open **Safari** → `https://your-app.onrender.com/app`
2. Tap **Share** (□↑) → **"Add to Home Screen"**
3. Maya AI installs as native iOS app! 🍎

**Android:**
1. Open **Chrome** → `https://your-app.onrender.com/app`
2. Tap **"Add to Home screen"** banner
3. Maya AI installs as Android app! 🤖

### 🔧 Local Development

```bash
# Clone repository
git clone https://github.com/stusseligmini/maya.git
cd maya

# Install dependencies
pip install -r requirements.txt

# Start development server
python main.py

# Access application
# Web: http://localhost:8000
# Mobile PWA: http://localhost:8000/app
# API Docs: http://localhost:8000/docs
```

## 🏗️ Architecture

### Microservices Design
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Maya API      │    │   AI Service    │    │  Worker Service │
│   (FastAPI)     │◄──►│   (Fooocus)     │◄──►│   (Celery)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │  Telegram Bot   │
│   (Database)    │    │   (Cache/Queue) │    │   (Review)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Directory Structure
```
📁 maya/
├── 📁 docker/                     # Container configuration
│   ├── Dockerfile                 # Main app container
│   ├── docker-compose.yml         # Service orchestration
│   └── services/                  # Individual service containers
│       ├── ai-service/            # Fooocus & ML models
│       ├── db-service/            # Database configuration
│       └── worker-service/        # Background job processing
├── 📁 config/                     # Environment & settings
│   ├── settings.py               # Application configuration
│   ├── secrets.py                # API keys & secrets
│   ├── dev.env                   # Development environment
│   └── prod.env                  # Production environment
├── 📁 database/                   # Database layer
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── connection.py             # Database connectivity
│   └── migrations/               # Database schema changes
├── 📁 api/                        # API endpoints
│   ├── routes.py                 # Main API routes
│   ├── auth.py                   # Authentication logic
│   └── clients/                  # External API clients
│       ├── openai_client.py      # OpenAI integration
│       ├── huggingface_client.py # Hugging Face models
│       └── runway_client.py      # Video generation
├── 📁 queue/                      # Background processing
│   ├── worker.py                 # Celery worker setup
│   ├── tasks.py                  # Background tasks
│   └── scheduler.py              # Scheduled jobs
├── 📁 telegram/                   # Telegram integration
│   ├── bot_image_review.py       # Image review bot
│   ├── bot_video_review.py       # Video review bot
│   └── callbacks/                # Bot callback handlers
├── 📁 moderation/                 # Content safety
│   ├── image_moderation.py       # Image content checks
│   ├── emotion_analysis.py       # Text sentiment analysis
│   └── platform_filter.py       # Platform-specific rules
├── 📁 processing/                 # Content manipulation
│   ├── caption_generator.py      # AI caption creation
│   ├── video_editor.py           # Video processing
│   ├── image_optimizer.py        # Image optimization
│   └── scheduler.py              # Publishing scheduler
├── 📁 publishing/                 # Platform publishing
│   ├── instagram_api.py          # Instagram integration
│   ├── tiktok_api.py             # TikTok integration
│   ├── twitter_api.py            # Twitter integration
│   ├── fanvue_upload.py          # Fanvue integration
│   └── snapchat_upload.py        # Snapchat integration
├── 📁 storage/                    # File management
│   ├── proton_upload.py          # Proton Drive backup
│   ├── backup_system.py          # Automated backups
│   └── privacy_guard.py          # Data protection
├── 📁 monitoring/                 # System monitoring
│   ├── health_checks.py          # Service health monitoring
│   ├── metrics.py                # Performance metrics
│   └── alerts.py                 # Alert notifications
├── 📁 input/                      # Content input directories
│   ├── images_raw/               # AI-generated images
│   ├── captions_raw/             # Generated captions
│   └── videos_raw/               # Generated videos
├── 📁 logs/                       # Application logs
├── 📁 tests/                      # Test suite
├── 📄 main.py                     # Application entry point
├── 📄 requirements.txt            # Python dependencies
└── 📄 README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL
- Redis

### 1. Clone Repository
```bash
git clone <repository-url>
cd maya
```

### 2. Environment Setup
```bash
# Copy environment file
cp config/dev.env .env

# Edit configuration
nano .env
```

### 3. Docker Setup
```bash
# Start all services
cd docker
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Initialize Database
```bash
# Run database migrations
docker-compose exec maya-api python init_db.py
```

### 5. Access Services
- **API Documentation**: http://localhost:8080/docs
- **Main Application**: http://localhost:8080
- **Celery Monitor**: http://localhost:5555
- **Health Check**: http://localhost:8080/health

## 📊 Content Processing Flow

```mermaid
graph TD
    A[Upload Content] --> B[Queue Processing]
    B --> C[Content Moderation]
    C --> D{Safe Content?}
    D -->|Yes| E[AI Analysis]
    D -->|No| F[Reject & Log]
    E --> G[Caption Generation]
    G --> H[Platform Optimization]
    H --> I[Telegram Review]
    I --> J{Approved?}
    J -->|Yes| K[Schedule Publishing]
    J -->|No| L[Edit/Regenerate]
    K --> M[Publish to Platforms]
    M --> N[Monitor Performance]
    L --> G
```

## 🔧 Configuration

### Environment Variables
```bash
# Core Settings
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql://maya:maya_secret@postgres:5432/maya_db
REDIS_URL=redis://redis:6379/0

# AI Services
OPENAI_API_KEY=your-openai-key
HUGGINGFACE_API_KEY=your-huggingface-key
FOOOCUS_API_URL=http://ai-service:8080

# Social Media APIs
INSTAGRAM_ACCESS_TOKEN=your-instagram-token
TIKTOK_ACCESS_TOKEN=your-tiktok-token
TWITTER_API_KEY=your-twitter-key

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# Security
JWT_SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
```

### Platform API Setup

#### Instagram
1. Create Facebook Developer Account
2. Create Instagram Business Account
3. Generate access token via Graph API
4. Add token to environment variables

#### TikTok
1. Register for TikTok for Developers
2. Create application and get credentials
3. Implement OAuth flow for user tokens

#### Twitter
1. Create Twitter Developer Account
2. Generate API keys and tokens
3. Configure OAuth 2.0 settings

## 🤖 API Usage

### Upload Content
```bash
curl -X POST "http://localhost:8080/api/content/upload" 
  -H "Authorization: Bearer YOUR_TOKEN" 
  -F "file=@image.jpg" 
  -F "metadata={"title":"Test Image","content_type":"image","target_platforms":["instagram","twitter"]}"
```

### Check Processing Status
```bash
curl "http://localhost:8080/api/queue/status" 
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Publish Content
```bash
curl -X POST "http://localhost:8080/api/content/123/publish" 
  -H "Authorization: Bearer YOUR_TOKEN" 
  -H "Content-Type: application/json" 
  -d '{"platforms":["instagram","twitter"],"schedule_time":"2024-01-01T14:00:00"}'
```

## 🔍 Monitoring & Debugging

### Health Checks
```bash
# System health
curl http://localhost:8080/health

# Service metrics
curl http://localhost:8080/metrics
```

### Log Monitoring
```bash
# Application logs
docker-compose logs -f maya-api

# Worker logs
docker-compose logs -f worker-service

# Database logs
docker-compose logs -f postgres
```

### Celery Monitoring
Visit http://localhost:5555 for real-time worker monitoring

## 🧪 Testing

### Run Tests
```bash
# Unit tests
docker-compose exec maya-api pytest tests/unit/

# Integration tests
docker-compose exec maya-api pytest tests/integration/

# End-to-end tests
docker-compose exec maya-api pytest tests/e2e/
```

### Manual Testing
```bash
# Test content upload
python scripts/test_upload.py

# Test moderation
python scripts/test_moderation.py

# Test publishing
python scripts/test_publishing.py
```

## 🔒 Security

### Authentication
- JWT token-based authentication
- Role-based access control
- API key management for external services

### Data Protection
- Encryption at rest and in transit
- GDPR compliance features
- Automatic data anonymization
- Secure API key storage

### Rate Limiting
- Per-user request limits
- Platform-specific rate limiting
- Automatic backoff and retry logic

## 📈 Performance Optimization

### Caching Strategy
- Redis for session and API response caching
- Image thumbnail caching
- Model prediction caching

### Database Optimization
- Connection pooling
- Query optimization
- Automatic indexing
- Read replicas for scaling

### Processing Optimization
- Async task processing
- Batch content processing
- Resource usage monitoring
- Auto-scaling workers

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database status
docker-compose ps postgres

# Reset database
docker-compose down
docker volume rm maya_postgres_data
docker-compose up -d postgres
```

#### Worker Not Processing Tasks
```bash
# Check worker status
docker-compose logs worker-service

# Restart workers
docker-compose restart worker-service

# Check Redis connection
docker-compose exec redis redis-cli ping
```

#### API Authentication Errors
```bash
# Verify JWT secret
echo $JWT_SECRET_KEY

# Check token generation
python scripts/generate_token.py
```

### Support Channels
- GitHub Issues: Technical problems and feature requests
- Documentation: Detailed guides and API reference
- Community Forum: Usage questions and best practices

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Run tests before committing
5. Submit pull request

### Code Standards
- Follow PEP 8 Python style guide
- Write comprehensive tests
- Document all functions and classes
- Use type hints consistently

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🏆 Acknowledgments

- **Fooocus**: AI image generation capabilities
- **OpenAI**: GPT models for content generation
- **Hugging Face**: ML model ecosystem
- **FastAPI**: High-performance web framework
- **Celery**: Distributed task processing
- **PostgreSQL**: Robust database system

---

## 🚀 Ready to Optimize Your Content?

Maya AI transforms your content creation workflow with intelligent automation. Get started today and experience the future of social media management!

**Need Help?** Check our [documentation](docs/) or open an [issue](https://github.com/your-repo/maya/issues).
