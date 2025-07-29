"""Command Line Interface for Maya AI Content System."""

import click
import asyncio
import sys
from typing import List, Optional
from datetime import datetime
import json

from maya.config.settings import get_settings
from maya.core.logging import configure_logging, get_logger
from maya.content.processor import ContentProcessor, ContentItem, ContentType, Platform
from maya.social.platforms import social_manager
from maya.ai.models import ai_manager
from maya.security.auth import password_manager, jwt_manager
from maya.api.integrations import n8n_router


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.pass_context
def cli(ctx, debug):
    """Maya AI Content System CLI."""
    ctx.ensure_object(dict)
    
    # Configure logging
    log_level = "DEBUG" if debug else "INFO"
    configure_logging(level=log_level, json_logs=False)
    
    ctx.obj['logger'] = get_logger("CLI")
    ctx.obj['logger'].info("Maya CLI started")


@cli.group()
def content():
    """Content processing commands."""
    pass


@content.command()
@click.option('--text', '-t', required=True, help='Content text to process')
@click.option('--platforms', '-p', multiple=True, default=['twitter'], 
              help='Target platforms (twitter, instagram, tiktok)')
@click.option('--analyze/--no-analyze', default=True, help='Enable AI analysis')
@click.option('--output', '-o', type=click.File('w'), default='-', help='Output file')
@click.pass_context
def process(ctx, text, platforms, analyze, output):
    """Process content for optimization."""
    
    async def _process():
        processor = ContentProcessor()
        
        content_item = ContentItem(
            id=None,
            content_type=ContentType.TEXT,
            text=text
        )
        
        platform_enums = []
        for platform in platforms:
            try:
                platform_enums.append(Platform(platform))
            except ValueError:
                ctx.obj['logger'].error(f"Unknown platform: {platform}")
                return
        
        result = await processor.process_content(content_item, platform_enums, analyze)
        
        # Output results
        output_data = result.to_dict()
        json.dump(output_data, output, indent=2, default=str)
        
        if output != sys.stdout:
            ctx.obj['logger'].info(f"Results written to {output.name}")
    
    try:
        asyncio.run(_process())
    except Exception as e:
        ctx.obj['logger'].error(f"Content processing failed: {str(e)}")
        sys.exit(1)


@content.command()
@click.option('--text', '-t', required=True, help='Content text to publish')
@click.option('--platforms', '-p', multiple=True, required=True,
              help='Target platforms (twitter, instagram)')
@click.option('--dry-run', is_flag=True, help='Simulate publishing without actually posting')
@click.pass_context
def publish(ctx, text, platforms, dry_run):
    """Publish content to social platforms."""
    
    async def _publish():
        content_item = ContentItem(
            id=f"cli_{int(datetime.utcnow().timestamp())}",
            content_type=ContentType.TEXT,
            text=text
        )
        
        platform_enums = []
        for platform in platforms:
            try:
                platform_enums.append(Platform(platform))
            except ValueError:
                ctx.obj['logger'].error(f"Unknown platform: {platform}")
                return
        
        if dry_run:
            ctx.obj['logger'].info("DRY RUN: Would publish to platforms", 
                                 platforms=platforms, text=text[:50] + "...")
            return
        
        results = await social_manager.publish_to_platforms(content_item, platform_enums)
        
        for platform, result in results.items():
            if result.status == "published":
                ctx.obj['logger'].info(f"Published to {platform.value}", 
                                     post_id=result.post_id)
            else:
                ctx.obj['logger'].error(f"Failed to publish to {platform.value}",
                                      error=result.metadata.get('error', 'Unknown error'))
    
    try:
        asyncio.run(_publish())
    except Exception as e:
        ctx.obj['logger'].error(f"Content publishing failed: {str(e)}")
        sys.exit(1)


@content.command()
@click.option('--text', '-t', required=True, help='Content text to schedule')
@click.option('--platforms', '-p', multiple=True, required=True,
              help='Target platforms (twitter, instagram)')
@click.option('--when', '-w', required=True, help='Publish time (YYYY-MM-DD HH:MM)')
@click.pass_context
def schedule(ctx, text, platforms, when):
    """Schedule content for future publishing."""
    
    async def _schedule():
        try:
            publish_time = datetime.strptime(when, '%Y-%m-%d %H:%M')
        except ValueError:
            ctx.obj['logger'].error("Invalid time format. Use YYYY-MM-DD HH:MM")
            return
        
        if publish_time <= datetime.utcnow():
            ctx.obj['logger'].error("Scheduled time must be in the future")
            return
        
        content_item = ContentItem(
            id=f"cli_scheduled_{int(datetime.utcnow().timestamp())}",
            content_type=ContentType.TEXT,
            text=text
        )
        
        platform_enums = []
        for platform in platforms:
            try:
                platform_enums.append(Platform(platform))
            except ValueError:
                ctx.obj['logger'].error(f"Unknown platform: {platform}")
                return
        
        results = await social_manager.schedule_for_platforms(
            content_item, platform_enums, publish_time
        )
        
        for platform, result in results.items():
            if result.status == "scheduled":
                ctx.obj['logger'].info(f"Scheduled for {platform.value}", 
                                     post_id=result.post_id,
                                     scheduled_time=result.scheduled_time)
            else:
                ctx.obj['logger'].error(f"Failed to schedule for {platform.value}",
                                      error=result.metadata.get('error', 'Unknown error'))
    
    try:
        asyncio.run(_schedule())
    except Exception as e:
        ctx.obj['logger'].error(f"Content scheduling failed: {str(e)}")
        sys.exit(1)


@cli.group()
def ai():
    """AI model commands."""
    pass


@ai.command()
@click.pass_context
def models(ctx):
    """List available AI models."""
    available_models = ai_manager.list_available_models()
    
    ctx.obj['logger'].info("Available AI models:")
    for model in available_models:
        click.echo(f"  - {model}")


@ai.command()
@click.option('--text', '-t', required=True, help='Text to analyze')
@click.option('--model', '-m', default='huggingface', help='AI model to use')
@click.option('--output', '-o', type=click.File('w'), default='-', help='Output file')
@click.pass_context
def analyze(ctx, text, model, output):
    """Analyze content using AI models."""
    
    async def _analyze():
        try:
            ai_model = ai_manager.get_model(model)
            analysis = await ai_model.analyze_content(text)
            
            json.dump(analysis, output, indent=2, default=str)
            
            if output != sys.stdout:
                ctx.obj['logger'].info(f"Analysis written to {output.name}")
                
        except Exception as e:
            ctx.obj['logger'].error(f"AI analysis failed: {str(e)}")
            raise
    
    try:
        asyncio.run(_analyze())
    except Exception as e:
        ctx.obj['logger'].error(f"AI analysis failed: {str(e)}")
        sys.exit(1)


@ai.command()
@click.option('--prompt', '-p', required=True, help='Prompt for content generation')
@click.option('--model', '-m', default='openai', help='AI model to use')
@click.option('--max-tokens', default=150, help='Maximum tokens to generate')
@click.pass_context
def generate(ctx, prompt, model, max_tokens):
    """Generate content using AI models."""
    
    async def _generate():
        try:
            ai_model = ai_manager.get_model(model)
            content = await ai_model.generate_content(prompt, max_tokens=max_tokens)
            
            click.echo(f"\nGenerated content:\n{content}\n")
            
        except Exception as e:
            ctx.obj['logger'].error(f"AI generation failed: {str(e)}")
            raise
    
    try:
        asyncio.run(_generate())
    except Exception as e:
        ctx.obj['logger'].error(f"AI generation failed: {str(e)}")
        sys.exit(1)


@cli.group()
def social():
    """Social platform commands."""
    pass


@social.command()
@click.pass_context
def platforms(ctx):
    """List supported social platforms."""
    supported_platforms = social_manager.list_supported_platforms()
    
    ctx.obj['logger'].info("Supported social platforms:")
    for platform in supported_platforms:
        click.echo(f"  - {platform.value}")


@social.command()
@click.option('--platform', '-p', help='Filter by platform')
@click.pass_context
def scheduled(ctx, platform):
    """List scheduled posts."""
    
    platform_enum = None
    if platform:
        try:
            platform_enum = Platform(platform)
        except ValueError:
            ctx.obj['logger'].error(f"Unknown platform: {platform}")
            return
    
    scheduled_posts = social_manager.get_scheduled_posts(platform_enum)
    
    if not scheduled_posts:
        click.echo("No scheduled posts found.")
        return
    
    click.echo("Scheduled posts:")
    for post in scheduled_posts:
        click.echo(f"  ID: {post.id}")
        click.echo(f"  Platform: {post.platform.value}")
        click.echo(f"  Scheduled: {post.scheduled_time}")
        click.echo(f"  Status: {post.status}")
        click.echo(f"  Content: {post.content.text[:50]}...")
        click.echo()


@cli.group()
def server():
    """Server management commands."""
    pass


@server.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
@click.pass_context
def start(ctx, host, port, reload):
    """Start the Maya API server."""
    import uvicorn
    
    ctx.obj['logger'].info(f"Starting Maya API server on {host}:{port}")
    
    uvicorn.run(
        "maya.api.app:app",
        host=host,
        port=port,
        reload=reload
    )


@cli.group()
def auth():
    """Authentication commands."""
    pass


@auth.command()
@click.option('--username', '-u', required=True, help='Username')
@click.option('--email', '-e', required=True, help='Email address')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Password')
@click.pass_context
def create_token(ctx, username, email, password):
    """Create an authentication token."""
    try:
        # In a real implementation, you'd verify credentials against a database
        # For demo purposes, we'll create a token for any valid input
        
        token = jwt_manager.create_access_token(
            user_id=f"user_{username}",
            username=username,
            email=email,
            scopes=["read", "write"]
        )
        
        click.echo(f"Access token: {token}")
        ctx.obj['logger'].info(f"Token created for user: {username}")
        
    except Exception as e:
        ctx.obj['logger'].error(f"Token creation failed: {str(e)}")
        sys.exit(1)


@auth.command()
@click.option('--length', default=16, help='Password length')
@click.pass_context
def generate_password(ctx, length):
    """Generate a secure password."""
    try:
        password = password_manager.generate_secure_password(length)
        click.echo(f"Generated password: {password}")
        
    except Exception as e:
        ctx.obj['logger'].error(f"Password generation failed: {str(e)}")
        sys.exit(1)


@cli.command()
@click.pass_context
def health(ctx):
    """Check system health."""
    
    async def _health_check():
        from maya.monitoring.metrics import health_monitor
        
        health_status = await health_monitor.run_all_health_checks()
        overall_health = health_monitor.get_overall_health()
        
        click.echo(f"Overall health: {overall_health}")
        click.echo("\nComponent health:")
        
        for name, check in health_status.items():
            status_icon = "✓" if check.status == "healthy" else "✗"
            click.echo(f"  {status_icon} {name}: {check.status}")
            
            if check.response_time_ms:
                click.echo(f"    Response time: {check.response_time_ms:.2f}ms")
            
            if check.details:
                click.echo(f"    Details: {check.details}")
    
    try:
        asyncio.run(_health_check())
    except Exception as e:
        ctx.obj['logger'].error(f"Health check failed: {str(e)}")
        sys.exit(1)


@cli.group()
def n8n():
    """n8n integration commands."""
    pass


@n8n.command()
@click.option('--url', default=None, help='n8n instance URL')
@click.option('--api-key', default=None, help='n8n API key')
@click.pass_context
def register(ctx, url, api_key):
    """Register Maya nodes in n8n."""
    from scripts.n8n_workflow_manager import register_maya_credential_type
    
    # Override settings if provided
    settings = get_settings()
    if url:
        settings.integrations.n8n_base_url = url
    if api_key:
        settings.integrations.n8n_api_key = api_key
    
    try:
        result = register_maya_credential_type()
        if result.get("success"):
            ctx.obj['logger'].info("Maya nodes registered successfully in n8n")
        else:
            ctx.obj['logger'].error(f"Node registration failed: {result.get('error')}")
            sys.exit(1)
    except Exception as e:
        ctx.obj['logger'].error(f"Node registration failed: {str(e)}")
        sys.exit(1)


@n8n.command()
@click.option('--name', required=True, help='Workflow name')
@click.option('--template', default='content-generation', 
              type=click.Choice(['content-generation', 'social-publishing', 'analytics-collection']),
              help='Workflow template')
@click.pass_context
def create_workflow(ctx, name, template):
    """Create a new n8n workflow from template."""
    from scripts.n8n_workflow_manager import create_workflow
    
    try:
        result = create_workflow(name, template)
        if result.get("success"):
            ctx.obj['logger'].info(f"Workflow '{name}' created successfully from template '{template}'")
        else:
            ctx.obj['logger'].error(f"Workflow creation failed: {result.get('error')}")
            sys.exit(1)
    except Exception as e:
        ctx.obj['logger'].error(f"Workflow creation failed: {str(e)}")
        sys.exit(1)


@n8n.command()
@click.option('--endpoint', default='webhook', help='Endpoint to test')
@click.option('--payload', default='{}', help='JSON payload to send')
@click.pass_context
def test(ctx, endpoint, payload):
    """Test n8n integration endpoints."""
    from scripts.n8n_workflow_manager import test_webhook
    
    try:
        result = test_webhook(endpoint, payload)
        if result.get("success"):
            ctx.obj['logger'].info(f"Endpoint test successful: {endpoint}")
            ctx.obj['logger'].info(f"Response: {json.dumps(result.get('response', {}), indent=2)}")
        else:
            ctx.obj['logger'].error(f"Endpoint test failed: {result.get('error')}")
            sys.exit(1)
    except Exception as e:
        ctx.obj['logger'].error(f"Endpoint test failed: {str(e)}")
        sys.exit(1)


def main():
    """CLI entry point."""
    cli()


if __name__ == '__main__':
    main()