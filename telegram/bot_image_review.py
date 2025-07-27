"""
Telegram bot for image review and approval workflow
"""
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from typing import Dict, Any
import json
import os

from ..config.secrets import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from ..database.models import ContentItem, ContentStatus
from ..database.connection import get_db_session
from ..services.content_service import ContentService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramImageReviewBot:
    def __init__(self):
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("Telegram bot token not configured")
        
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.app = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        self.content_service = ContentService()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        await update.message.reply_text(
            "🤖 Maya AI Content Review Bot\n\n"
            "I'll send you content for review and approval.\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/status - Show pending reviews"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show pending review status"""
        try:
            with get_db_session() as db:
                pending_count = db.query(ContentItem).filter(
                    ContentItem.status == ContentStatus.PENDING
                ).count()
                
                processing_count = db.query(ContentItem).filter(
                    ContentItem.status == ContentStatus.PROCESSING
                ).count()
            
            await update.message.reply_text(
                f"📊 Review Status\n\n"
                f"⏳ Pending Review: {pending_count}\n"
                f"🔄 Processing: {processing_count}\n"
                f"✅ Ready for approval workflow"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {str(e)}")
    
    async def send_content_for_review(
        self, 
        content_id: int, 
        image_path: str, 
        caption: str, 
        metadata: Dict[str, Any]
    ):
        """Send content to Telegram for review"""
        try:
            # Create approval buttons
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{content_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{content_id}")
                ],
                [
                    InlineKeyboardButton("✏️ Edit Caption", callback_data=f"edit_{content_id}"),
                    InlineKeyboardButton("🔄 Regenerate", callback_data=f"regenerate_{content_id}")
                ],
                [
                    InlineKeyboardButton("📊 View Details", callback_data=f"details_{content_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Prepare message text
            message_text = (
                f"🖼️ **New Content for Review**\n\n"
                f"**ID:** {content_id}\n"
                f"**Type:** {metadata.get('content_type', 'Unknown')}\n"
                f"**Title:** {metadata.get('title', 'No title')}\n\n"
                f"**Generated Caption:**\n{caption}\n\n"
                f"**Target Platforms:** {', '.join(metadata.get('target_platforms', []))}\n"
                f"**Keywords:** {metadata.get('target_keywords', 'None')}\n\n"
                f"Please review and choose an action:"
            )
            
            # Send image with caption and buttons
            if os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    await self.app.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=photo,
                        caption=message_text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
            else:
                # Send text message if image not found
                await self.app.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"⚠️ Image not found\n\n{message_text}",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            
            logger.info(f"Sent content {content_id} for Telegram review")
            
        except Exception as e:
            logger.error(f"Failed to send content {content_id} for review: {str(e)}")
            raise
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        try:
            # Parse callback data
            action, content_id = query.data.split('_', 1)
            content_id = int(content_id)
            
            if action == "approve":
                await self.approve_content(content_id, query)
            elif action == "reject":
                await self.reject_content(content_id, query)
            elif action == "edit":
                await self.edit_caption(content_id, query)
            elif action == "regenerate":
                await self.regenerate_content(content_id, query)
            elif action == "details":
                await self.show_details(content_id, query)
            else:
                await query.edit_message_text("❌ Unknown action")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
            logger.error(f"Callback handling error: {str(e)}")
    
    async def approve_content(self, content_id: int, query):
        """Approve content for publishing"""
        try:
            await self.content_service.approve_content(content_id, user_id=1)  # System user
            
            # Update message
            await query.edit_message_text(
                f"✅ Content {content_id} approved!\n\n"
                f"Content has been moved to the publishing queue.",
                parse_mode='Markdown'
            )
            
            # Trigger publishing workflow
            from ..queue.tasks import schedule_publishing_task
            schedule_publishing_task.delay(content_id, ["instagram"], None, 1)
            
        except Exception as e:
            await query.edit_message_text(f"❌ Approval failed: {str(e)}")
    
    async def reject_content(self, content_id: int, query):
        """Reject content"""
        try:
            await self.content_service.reject_content(
                content_id, 
                reason="Rejected via Telegram review", 
                user_id=1
            )
            
            await query.edit_message_text(
                f"❌ Content {content_id} rejected.\n\n"
                f"Content has been marked as rejected and will not be published."
            )
            
        except Exception as e:
            await query.edit_message_text(f"❌ Rejection failed: {str(e)}")
    
    async def edit_caption(self, content_id: int, query):
        """Edit caption (placeholder - would need text input handler)"""
        await query.edit_message_text(
            f"✏️ Caption editing for content {content_id}\n\n"
            f"To edit the caption, please use the web interface or send the new caption "
            f"as a reply to this message with format:\n"
            f"`/edit_caption {content_id} Your new caption here`",
            parse_mode='Markdown'
        )
    
    async def regenerate_content(self, content_id: int, query):
        """Regenerate content analysis"""
        try:
            # Trigger content reprocessing
            from ..queue.tasks import process_content_task
            task = process_content_task.delay(content_id, 1)
            
            await query.edit_message_text(
                f"🔄 Regenerating content {content_id}...\n\n"
                f"Task ID: {task.id}\n"
                f"This may take a few minutes. You'll receive a new review request when complete."
            )
            
        except Exception as e:
            await query.edit_message_text(f"❌ Regeneration failed: {str(e)}")
    
    async def show_details(self, content_id: int, query):
        """Show detailed content information"""
        try:
            with get_db_session() as db:
                content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
                
                if not content:
                    await query.edit_message_text("❌ Content not found")
                    return
                
                details = (
                    f"📊 **Content Details - ID {content_id}**\n\n"
                    f"**Title:** {content.title}\n"
                    f"**Type:** {content.content_type.value}\n"
                    f"**Status:** {content.status.value}\n"
                    f"**Created:** {content.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                    f"**Description:** {content.description or 'None'}\n"
                    f"**Keywords:** {content.target_keywords or 'None'}\n"
                    f"**Platforms:** {', '.join(content.target_platforms or [])}\n\n"
                )
                
                # Add AI analysis if available
                if content.ai_analysis:
                    details += (
                        f"**AI Analysis:**\n"
                        f"- Sentiment: {content.ai_analysis.sentiment_score or 'N/A'}\n"
                        f"- Engagement Prediction: {content.ai_analysis.engagement_prediction or 'N/A'}\n"
                        f"- Model: {content.ai_analysis.model_version or 'N/A'}\n\n"
                    )
                
                # Add moderation results if available
                if content.moderation_results:
                    mod_result = content.moderation_results[0]
                    details += (
                        f"**Moderation:**\n"
                        f"- Result: {mod_result.result.value}\n"
                        f"- NSFW Score: {mod_result.nsfw_score}\n"
                        f"- Auto Moderated: {mod_result.auto_moderated}\n"
                    )
                
                await query.edit_message_text(details, parse_mode='Markdown')
                
        except Exception as e:
            await query.edit_message_text(f"❌ Error getting details: {str(e)}")
    
    async def send_video_for_review(
        self, 
        content_id: int, 
        video_path: str, 
        title: str, 
        metadata: Dict[str, Any]
    ):
        """Send video content for review"""
        try:
            # Similar to image review but for videos
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{content_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{content_id}")
                ],
                [
                    InlineKeyboardButton("✏️ Edit Title", callback_data=f"edit_{content_id}"),
                    InlineKeyboardButton("🎬 Re-edit Video", callback_data=f"reedit_{content_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message_text = (
                f"🎬 **New Video for Review**\n\n"
                f"**ID:** {content_id}\n"
                f"**Title:** {title}\n"
                f"**Duration:** {metadata.get('duration', 'Unknown')}\n"
                f"**Target Platforms:** {', '.join(metadata.get('target_platforms', []))}\n\n"
                f"Please review and choose an action:"
            )
            
            if os.path.exists(video_path):
                with open(video_path, 'rb') as video:
                    await self.app.bot.send_video(
                        chat_id=self.chat_id,
                        video=video,
                        caption=message_text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
            else:
                await self.app.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"⚠️ Video not found\n\n{message_text}",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Failed to send video {content_id} for review: {str(e)}")
            raise
    
    def start_bot(self):
        """Start the Telegram bot"""
        logger.info("Starting Telegram bot...")
        self.app.run_polling()
    
    async def stop_bot(self):
        """Stop the Telegram bot"""
        logger.info("Stopping Telegram bot...")
        await self.app.stop()

# Global bot instance
telegram_bot = TelegramImageReviewBot() if TELEGRAM_BOT_TOKEN else None

async def send_for_telegram_review(content_id: int, file_path: str, caption: str, metadata: Dict[str, Any]):
    """Helper function to send content for Telegram review"""
    if not telegram_bot:
        logger.warning("Telegram bot not configured, skipping review")
        return
    
    try:
        if metadata.get('content_type') == 'video':
            await telegram_bot.send_video_for_review(content_id, file_path, caption, metadata)
        else:
            await telegram_bot.send_content_for_review(content_id, file_path, caption, metadata)
    except Exception as e:
        logger.error(f"Failed to send content {content_id} for Telegram review: {str(e)}")
        raise
