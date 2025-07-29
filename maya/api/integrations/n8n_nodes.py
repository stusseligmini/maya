"""
n8n Node Descriptions for Maya AI.

This module provides JSON descriptions for n8n custom nodes to interact with Maya AI.
These descriptions can be used to build custom n8n nodes for the Maya AI API.
"""

MAYA_NODE_DESCRIPTION = {
    "name": "Maya AI",
    "displayName": "Maya AI",
    "icon": "file:maya.svg",
    "group": ["transform"],
    "version": 1,
    "subtitle": "Optimize content with Maya AI",
    "description": "Interact with Maya AI to process, generate and analyze content",
    "defaults": {
        "name": "Maya AI"
    },
    "inputs": ["main"],
    "outputs": ["main"],
    "credentials": [
        {
            "name": "mayaApi",
            "required": True
        }
    ],
    "properties": [
        {
            "displayName": "Operation",
            "name": "operation",
            "type": "options",
            "options": [
                {
                    "name": "Process Content",
                    "value": "processContent"
                },
                {
                    "name": "Generate Content",
                    "value": "generateContent"
                },
                {
                    "name": "Analyze Content",
                    "value": "analyzeContent"
                },
                {
                    "name": "Get Platform Specs",
                    "value": "getPlatformSpecs"
                }
            ],
            "default": "processContent",
            "description": "The operation to perform"
        },
        
        # Process Content Fields
        {
            "displayName": "Content Data",
            "name": "contentData",
            "type": "json",
            "default": {},
            "description": "The content data to process",
            "displayOptions": {
                "show": {
                    "operation": [
                        "processContent"
                    ]
                }
            }
        },
        {
            "displayName": "Target Platforms",
            "name": "targetPlatforms",
            "type": "multiOptions",
            "options": [
                {
                    "name": "Twitter",
                    "value": "twitter"
                },
                {
                    "name": "Instagram",
                    "value": "instagram"
                },
                {
                    "name": "TikTok",
                    "value": "tiktok"
                },
                {
                    "name": "Facebook",
                    "value": "facebook"
                },
                {
                    "name": "LinkedIn",
                    "value": "linkedin"
                }
            ],
            "default": ["twitter", "instagram"],
            "description": "The target platforms to optimize for",
            "displayOptions": {
                "show": {
                    "operation": [
                        "processContent"
                    ]
                }
            }
        },
        {
            "displayName": "Analyze with AI",
            "name": "analyzeWithAI",
            "type": "boolean",
            "default": True,
            "description": "Whether to analyze the content with AI",
            "displayOptions": {
                "show": {
                    "operation": [
                        "processContent"
                    ]
                }
            }
        },
        
        # Generate Content Fields
        {
            "displayName": "Prompt",
            "name": "prompt",
            "type": "string",
            "default": "",
            "description": "The prompt to generate content from",
            "displayOptions": {
                "show": {
                    "operation": [
                        "generateContent"
                    ]
                }
            }
        },
        {
            "displayName": "Model Type",
            "name": "modelType",
            "type": "options",
            "options": [
                {
                    "name": "OpenAI",
                    "value": "openai"
                },
                {
                    "name": "HuggingFace",
                    "value": "huggingface"
                },
                {
                    "name": "Runway",
                    "value": "runway"
                }
            ],
            "default": "openai",
            "description": "The AI model to use for generation",
            "displayOptions": {
                "show": {
                    "operation": [
                        "generateContent"
                    ]
                }
            }
        },
        {
            "displayName": "Max Tokens",
            "name": "maxTokens",
            "type": "number",
            "default": 150,
            "description": "The maximum number of tokens to generate",
            "displayOptions": {
                "show": {
                    "operation": [
                        "generateContent"
                    ]
                }
            }
        },
        {
            "displayName": "Temperature",
            "name": "temperature",
            "type": "number",
            "default": 0.7,
            "description": "The temperature for generation (0-1)",
            "displayOptions": {
                "show": {
                    "operation": [
                        "generateContent"
                    ]
                }
            }
        },
        
        # Analyze Content Fields
        {
            "displayName": "Content",
            "name": "content",
            "type": "string",
            "default": "",
            "description": "The content to analyze",
            "displayOptions": {
                "show": {
                    "operation": [
                        "analyzeContent"
                    ]
                }
            }
        },
        {
            "displayName": "Model Types",
            "name": "modelTypes",
            "type": "multiOptions",
            "options": [
                {
                    "name": "OpenAI",
                    "value": "openai"
                },
                {
                    "name": "HuggingFace",
                    "value": "huggingface"
                }
            ],
            "default": ["openai"],
            "description": "The AI models to use for analysis",
            "displayOptions": {
                "show": {
                    "operation": [
                        "analyzeContent"
                    ]
                }
            }
        }
    ]
}

MAYA_TRIGGER_DESCRIPTION = {
    "name": "Maya AI Trigger",
    "displayName": "Maya AI Trigger",
    "icon": "file:maya.svg",
    "group": ["trigger"],
    "version": 1,
    "subtitle": "Trigger workflows from Maya AI",
    "description": "Starts the workflow when Maya AI sends a webhook",
    "defaults": {
        "name": "Maya AI Trigger"
    },
    "inputs": [],
    "outputs": ["main"],
    "credentials": [
        {
            "name": "mayaApi",
            "required": True
        }
    ],
    "webhooks": [
        {
            "name": "default",
            "httpMethod": "POST",
            "responseMode": "onReceived",
            "path": "maya-webhook"
        }
    ],
    "properties": [
        {
            "displayName": "Trigger Type",
            "name": "triggerType",
            "type": "options",
            "options": [
                {
                    "name": "Content Processed",
                    "value": "contentProcessed"
                },
                {
                    "name": "Content Generated",
                    "value": "contentGenerated"
                },
                {
                    "name": "Content Analysis Completed",
                    "value": "contentAnalyzed"
                }
            ],
            "default": "contentProcessed",
            "description": "The type of event to trigger on"
        }
    ]
}

# Export the node descriptions
node_descriptions = {
    "maya": MAYA_NODE_DESCRIPTION,
    "mayaTrigger": MAYA_TRIGGER_DESCRIPTION
}
