# Maya - AI Content Optimization for Social Platforms

Maya is an advanced AI system for optimizing content across social media platforms. It uses machine learning to analyze, enhance, and schedule content for maximum engagement.

## Features

- **FastAPI-based RESTful API** for content management and AI processing
- **Multi-platform Support** - Instagram, TikTok, Twitter/X optimization
- **AI Model Integration** - OpenAI, HuggingFace, Runway ML support
- **Content Processing Pipeline** - Image/video enhancement and moderation
- **User Authentication** - JWT-based secure authentication
- **Docker Support** - Containerized development and deployment
- **Database Integration** - SQLAlchemy with PostgreSQL/SQLite support

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)
- PostgreSQL (for production) or SQLite (for development)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd maya
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python init_db.py
```

5. Start the development server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Docker Development

```bash
# Start all services
docker-compose up

# Start specific services
docker-compose up maya-api postgres redis
```

## API Documentation

Once the server is running, visit:
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

## Architecture Overview

The system follows a modern microservices architecture:

- **API Gateway**: Centralized request routing and authentication
- **Database Layer**: SQLAlchemy models with PostgreSQL/SQLite
- **AI Integration**: Pluggable AI service providers
- **Content Pipeline**: Processing, optimization, and moderation
- **Platform Integration**: Multi-platform publishing support

## Key Components

### Authentication
- JWT-based authentication system
- User registration and login
- Role-based access control

### Content Management
- Upload and organize media content
- Version control for different platform optimizations
- Metadata and tagging system

### AI Processing
- Multiple AI provider support (OpenAI, HuggingFace, Runway)
- Asynchronous job processing
- Quality scoring and enhancement

### Platform Integration
- Instagram, TikTok, Twitter/X specifications
- Platform-specific optimization
- Automated content adaptation

## Configuration

Key configuration options in `.env`:

```env
# Application
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=sqlite:///./maya.db

# AI Services (optional)
OPENAI_API_KEY=your-key
HUGGINGFACE_API_KEY=your-key
RUNWAY_API_KEY=your-key

# Social Platforms (optional)
INSTAGRAM_CLIENT_ID=your-id
TWITTER_API_KEY=your-key
TIKTOK_CLIENT_ID=your-id
```

## Development

### Project Structure

```
maya/
├── app/                    # Application package
│   ├── api/               # API route modules
│   ├── auth/              # Authentication system
│   ├── models/            # Database models
│   └── services/          # Business logic services
├── config/                # Configuration management
├── database/              # Database connection and setup
├── main.py               # Application entry point
├── init_db.py            # Database initialization
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
└── docker-compose.yml   # Multi-service setup
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests (when available)
pytest
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

#### Content Management
- `POST /api/v1/content/` - Create content
- `GET /api/v1/content/` - List user content
- `GET /api/v1/content/{id}` - Get content details
- `POST /api/v1/content/{id}/upload` - Upload content file

#### AI Processing
- `GET /api/v1/ai/models` - List available AI models
- `POST /api/v1/ai/process` - Create processing job
- `GET /api/v1/ai/jobs` - List processing jobs
- `GET /api/v1/ai/jobs/{id}` - Get job status

## Deployment

### Production Setup

1. Configure production environment:
```env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@host:5432/maya
SECRET_KEY=your-production-secret
```

2. Build and deploy with Docker:
```bash
docker-compose -f docker-compose.yml --profile production up
```

### Monitoring

The system includes built-in monitoring:
- Health checks at `/health`
- Structured logging with structlog
- Prometheus metrics (optional)
- Grafana dashboards (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the configuration options in `.env.example`
