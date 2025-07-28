# 🤖 Maya AI + n8n Integration Guide

## 🔄 Automated Workflow with n8n

Maya AI integrates seamlessly with n8n for complete automation of your content creation and publishing pipeline.

### 🚀 Quick Setup

1. **Start the stack:**
```bash
docker-compose up -d
```

2. **Access n8n dashboard:**
```
http://localhost:5678
```
- Username: `maya`
- Password: `maya123`

### 📋 Pre-built Workflows

#### 1. Content Generation Workflow
- **Trigger**: Schedule (daily/weekly)
- **Action**: Generate AI content via Maya AI API
- **Output**: Save to database, send to moderation

#### 2. Social Media Publishing
- **Trigger**: Content approved in Maya AI
- **Action**: Auto-publish to platforms
- **Platforms**: Instagram, TikTok, Twitter, etc.

#### 3. Analytics Collection
- **Trigger**: Content published
- **Action**: Collect performance metrics
- **Output**: Update Maya AI analytics dashboard

### 🔗 Maya AI + n8n Endpoints

n8n can interact with Maya AI through these APIs:

```javascript
// Content Generation
POST http://maya-ai:8000/api/content/generate
{
  "prompt": "Generate vacation content",
  "platform": "instagram",
  "style": "professional"
}

// Get Content Status
GET http://maya-ai:8000/api/content/{id}/status

// Publish Content
POST http://maya-ai:8000/api/content/{id}/publish
{
  "platforms": ["instagram", "tiktok"]
}
```

### 📊 Monitoring Stack

The complete monitoring setup includes:

- **Maya AI**: Main application (port 8000)
- **n8n**: Workflow automation (port 5678)
- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Dashboards (port 3000)
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache (port 6379)

### 🎯 Example n8n Workflow

```json
{
  "name": "Maya AI Daily Content",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": {
          "hour": 9,
          "minute": 0
        }
      }
    },
    {
      "name": "Generate Content",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://maya-ai:8000/api/content/generate",
        "method": "POST",
        "body": {
          "prompt": "Daily motivation post",
          "platform": "instagram"
        }
      }
    },
    {
      "name": "Wait for Approval",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "time": 1800
      }
    },
    {
      "name": "Publish Content",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://maya-ai:8000/api/content/{{$json.id}}/publish",
        "method": "POST"
      }
    }
  ]
}
```

### 🔧 Custom Integrations

You can create custom n8n nodes for:

- **Platform-specific posting** (Instagram, TikTok, etc.)
- **AI model selection** (OpenAI, HuggingFace, etc.)
- **Content moderation** with custom rules
- **Performance analytics** collection
- **Telegram notifications** for approvals

### 🎉 Benefits

- ✅ **Full Automation** - Set and forget content pipeline
- ✅ **Visual Workflows** - Easy to understand and modify
- ✅ **Scalable** - Handle multiple accounts and platforms
- ✅ **Monitoring** - Complete observability stack
- ✅ **Flexible** - Custom integrations and workflows

Start your automated content empire with Maya AI + n8n! 🚀
