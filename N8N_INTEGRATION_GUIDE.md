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

3. **Register Maya Nodes in n8n:**
```bash
python -m scripts.n8n_workflow_manager register
```

### 📋 Pre-built Workflows

#### 1. Content Generation Workflow
Install the pre-built workflow:
```bash
python -m scripts.n8n_workflow_manager create "Daily Content Generation" --template content-generation
```

#### 2. Social Media Publishing
Install the pre-built workflow:
```bash
python -m scripts.n8n_workflow_manager create "Social Media Publishing" --template social-publishing
```

#### 3. Analytics Collection
Install the pre-built workflow:
```bash
python -m scripts.n8n_workflow_manager create "Analytics Collection" --template analytics-collection
```

### 🔗 Maya AI + n8n Endpoints

n8n can interact with Maya AI through these API endpoints:

```
# Webhook endpoint for n8n
POST /api/integrations/n8n/webhook
{
  "action": "process_content",
  "content_data": {...},
  "target_platforms": ["twitter", "instagram"],
  "analyze_with_ai": true
}

# Background task submission
POST /api/integrations/n8n/task
{
  "task_type": "content_generation",
  "parameters": {...}
}

# Platform specifications
GET /api/integrations/n8n/platform-specs

# Health check
GET /api/integrations/n8n/health
```

### 📊 Monitoring Stack

The complete monitoring setup includes:

- **Maya AI**: Main application (port 8000)
- **n8n**: Workflow automation (port 5678)
- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Dashboards (port 3000)
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache (port 6379)

### 🎯 Example n8n Node

Maya AI provides custom n8n nodes for easy integration:

```javascript
// Maya AI Node
{
  "name": "Maya AI",
  "displayName": "Maya AI",
  "group": ["transform"],
  "version": 1,
  "description": "Interact with Maya AI to process, generate and analyze content",
  "defaults": {
    "name": "Maya AI"
  },
  "inputs": ["main"],
  "outputs": ["main"],
  "credentials": [
    {
      "name": "mayaApi",
      "required": true
    }
  ],
  "properties": [
    {
      "displayName": "Operation",
      "name": "operation",
      "type": "options",
      "options": [
        {"name": "Process Content", "value": "processContent"},
        {"name": "Generate Content", "value": "generateContent"},
        {"name": "Analyze Content", "value": "analyzeContent"},
        {"name": "Get Platform Specs", "value": "getPlatformSpecs"}
      ],
      "default": "processContent"
    },
    // Additional properties based on operation...
  ]
}
```

### 🔧 Custom Integration Features

The Maya AI n8n integration includes:

- **Webhooks** - Trigger workflows from Maya AI events
- **Custom Nodes** - Dedicated Maya AI nodes for n8n
- **Background Tasks** - Submit long-running jobs to Maya AI
- **Authentication** - Secure API access with tokens
- **Error Handling** - Robust error management and reporting

### 🎉 Benefits

- ✅ **Full Automation** - Set and forget content pipeline
- ✅ **Visual Workflows** - Easy to understand and modify
- ✅ **Scalable** - Handle multiple accounts and platforms
- ✅ **Monitoring** - Complete observability stack
- ✅ **Flexible** - Custom integrations and workflows

### 🛠️ Troubleshooting

If you encounter issues with the integration:

1. Check the Maya API health endpoint: `GET /api/integrations/n8n/health`
2. Verify n8n webhook credentials and secrets
3. Check the Maya logs for detailed error information
4. Run the test webhook command:
   ```bash
   python -m scripts.n8n_workflow_manager test --payload '{"action":"generate_content","prompt":"test"}'
   ```

Start your automated content empire with Maya AI + n8n! 🚀
