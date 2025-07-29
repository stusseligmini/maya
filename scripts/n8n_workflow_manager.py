"""
n8n workflow manager for Maya AI.

This script helps with setting up and managing n8n workflows for Maya AI.
It can be used to bootstrap new workflows and test the integration.
"""

import argparse
import json
import os
import requests
import sys
from typing import Dict, Any, List, Optional

# Make sure we can import from the Maya package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from maya.config.settings import get_settings

settings = get_settings()


def setup_workflow_parser():
    """Set up argument parser for the workflow manager."""
    parser = argparse.ArgumentParser(description="Maya AI n8n Workflow Manager")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create workflow command
    create_parser = subparsers.add_parser("create", help="Create a new n8n workflow")
    create_parser.add_argument("name", help="The name of the workflow")
    create_parser.add_argument("--template", help="Template workflow to use", 
                              choices=["content-generation", "social-publishing", "analytics-collection"],
                              default="content-generation")
    
    # List workflows command
    list_parser = subparsers.add_parser("list", help="List all workflows")
    
    # Test webhook command
    test_parser = subparsers.add_parser("test", help="Test the n8n webhook integration")
    test_parser.add_argument("--endpoint", help="The endpoint to test", default="webhook")
    test_parser.add_argument("--payload", help="The JSON payload to send", default="{}")
    
    # Register Maya AI as a credential type in n8n
    register_parser = subparsers.add_parser("register", help="Register Maya AI as a credential type in n8n")
    
    return parser


def get_n8n_api_url(path: str) -> str:
    """Get the full URL for an n8n API endpoint."""
    return f"{settings.integrations.n8n_base_url}/api/{path}"


def get_auth_headers() -> Dict[str, str]:
    """Get the authentication headers for the n8n API."""
    headers = {
        "Content-Type": "application/json"
    }
    
    if settings.integrations.n8n_api_key:
        headers["X-N8N-API-KEY"] = settings.integrations.n8n_api_key
    
    return headers


def create_workflow(name: str, template: str) -> Dict[str, Any]:
    """Create a new workflow in n8n from a template."""
    # Get the template workflow
    template_path = os.path.join(
        os.path.dirname(__file__), 
        "templates", 
        f"{template}.json"
    )
    
    if not os.path.exists(template_path):
        print(f"Error: Template {template} not found")
        available_templates = [
            os.path.splitext(f)[0] 
            for f in os.listdir(os.path.join(os.path.dirname(__file__), "templates"))
            if f.endswith(".json")
        ]
        print(f"Available templates: {', '.join(available_templates)}")
        return {"success": False, "error": "Template not found"}
    
    try:
        with open(template_path, "r") as f:
            workflow_data = json.load(f)
        
        # Update the name
        workflow_data["name"] = name
        
        # Create the workflow
        response = requests.post(
            get_n8n_api_url("workflows"),
            headers=get_auth_headers(),
            json=workflow_data
        )
        
        if response.status_code in (200, 201):
            print(f"Workflow {name} created successfully")
            return {"success": True, "workflow": response.json()}
        else:
            print(f"Error creating workflow: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text}
            
    except Exception as e:
        print(f"Error creating workflow: {str(e)}")
        return {"success": False, "error": str(e)}


def list_workflows() -> Dict[str, Any]:
    """List all workflows in n8n."""
    try:
        response = requests.get(
            get_n8n_api_url("workflows"),
            headers=get_auth_headers()
        )
        
        if response.status_code == 200:
            workflows = response.json()
            print(f"Found {len(workflows)} workflows:")
            for wf in workflows:
                print(f"- {wf['name']} (ID: {wf['id']})")
            return {"success": True, "workflows": workflows}
        else:
            print(f"Error listing workflows: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text}
            
    except Exception as e:
        print(f"Error listing workflows: {str(e)}")
        return {"success": False, "error": str(e)}


def test_webhook(endpoint: str, payload: str) -> Dict[str, Any]:
    """Test the n8n webhook integration."""
    try:
        # Parse the payload
        payload_data = json.loads(payload)
        
        # Send the request to the Maya API
        maya_url = f"http://localhost:{settings.api_port}/api/integrations/n8n/{endpoint}"
        print(f"Testing webhook: {maya_url}")
        print(f"Payload: {json.dumps(payload_data, indent=2)}")
        
        response = requests.post(
            maya_url,
            json=payload_data,
            headers={
                "Content-Type": "application/json",
                "X-N8N-Signature": "test-signature"  # This would be ignored in test mode
            }
        )
        
        print(f"Response: {response.status_code} - {response.text}")
        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
        }
            
    except Exception as e:
        print(f"Error testing webhook: {str(e)}")
        return {"success": False, "error": str(e)}


def register_maya_credential_type() -> Dict[str, Any]:
    """Register Maya AI as a credential type in n8n."""
    credential_type = {
        "name": "mayaApi",
        "displayName": "Maya AI API",
        "properties": [
            {
                "displayName": "API URL",
                "name": "apiUrl",
                "type": "string",
                "default": "http://maya-ai:8000",
                "description": "URL of the Maya AI API"
            },
            {
                "displayName": "API Key",
                "name": "apiKey",
                "type": "string",
                "description": "API Key for authenticating with Maya AI"
            }
        ]
    }
    
    try:
        response = requests.post(
            get_n8n_api_url("credentials/schema"),
            headers=get_auth_headers(),
            json=credential_type
        )
        
        if response.status_code in (200, 201):
            print("Maya AI credential type registered successfully")
            return {"success": True, "credential_type": response.json()}
        else:
            print(f"Error registering credential type: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text}
            
    except Exception as e:
        print(f"Error registering credential type: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    """Main entry point for the workflow manager."""
    parser = setup_workflow_parser()
    args = parser.parse_args()
    
    if args.command == "create":
        create_workflow(args.name, args.template)
    elif args.command == "list":
        list_workflows()
    elif args.command == "test":
        test_webhook(args.endpoint, args.payload)
    elif args.command == "register":
        register_maya_credential_type()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
