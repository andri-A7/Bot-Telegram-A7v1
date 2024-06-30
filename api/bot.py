import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers.command_handlers import start, view_airdrops, add_airdrop_handler, edit_airdrop_handler, delete_airdrop_handler, leaderboard
from handlers.message_handlers import handle_message, button_handler
from utils.logger import setup_logging
from database.DbContext import db
import json

# Load environment variables
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

def main() -> Application:
    setup_logging()
    
    application = Application.builder().token(TOKEN).build()
    application.bot_data['ADMIN_ID'] = ADMIN_ID

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("view", view_airdrops))
    application.add_handler(CommandHandler("add", add_airdrop_handler))
    application.add_handler(CommandHandler("edit", edit_airdrop_handler))
    application.add_handler(CommandHandler("delete", delete_airdrop_handler))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))

    return application

# Handler function for Vercel
def handler(event, context):
    application = main()
    
    # Process the incoming request as a Telegram update
    if event.get("httpMethod") == "POST":
        data = json.loads(event.get("body"))
        update = Update.de_json(data, application.bot)
        application.update_queue.put(update)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Webhook received and processed')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from bot')
    }
