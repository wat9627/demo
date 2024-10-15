   
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ContextTypes # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import csv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
TWITTER, WALLET = range(2)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! Welcome to the Airdrop Bot.\n\n"
        "To participate in the airdrop, please follow these steps:\n"
        "1. Follow our Twitter account: @YourProjectTwitter\n"
        "2. Provide your Twitter username\n"
        "3. Provide your wallet address\n\n"
        "Click the button below to start.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Start Airdrop", callback_data='start_airdrop')]
        ])
    )
    return ConversationHandler.END

async def start_airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Great! Please provide your Twitter username.")
    return TWITTER

async def twitter_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    context.user_data['twitter'] = update.message.text
    await update.message.reply_text("Thanks! Now, please provide your wallet address.")
    return WALLET

async def wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    context.user_data['wallet'] = update.message.text
    
    # Save user data
    save_user_data(user.id, user.username, context.user_data['twitter'], context.user_data['wallet'])
    
    await update.message.reply_text("Thank you for participating in the airdrop! We've recorded your information.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Airdrop participation cancelled.")
    return ConversationHandler.END

def save_user_data(user_id, username, twitter, wallet):
    with open('airdrop_participants.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, username, twitter, wallet])

def main() -> None:
    # Create the Application and pass it your bot's token
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_airdrop, pattern='^start_airdrop$')],
        states={
            TWITTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, twitter_username)],
            WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, wallet_address)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()