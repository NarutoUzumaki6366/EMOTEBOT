import logging
from typing import List, Optional
import requests
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Bot Configuration
BOT_TOKEN = "8538441981:AAHBirTq9VeUPACBFd2D8KsTeDevvTB2Lk8"
OWNER_ID = 6710024903  # Your Telegram User ID here
ALLOWED_GROUPS = set()  # Will store allowed group IDs

# API Configuration
API_CONFIG_FILE = "api_config.json"
EMOTE_API_URL = ""  # Will be loaded from config file

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_api_config():
    """Load API configuration from JSON file."""
    global EMOTE_API_URL
    
    if os.path.exists(API_CONFIG_FILE):
        try:
            with open(API_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                EMOTE_API_URL = config.get('api_url', '')
                logger.info(f"API config loaded: {EMOTE_API_URL}")
                return True
        except Exception as e:
            logger.error(f"Error loading API config: {e}")
            return False
    else:
        # Create default config file
        default_config = {'api_url': 'https://come-championships-fig-portal.trycloudflare.com/join'}
        try:
            with open(API_CONFIG_FILE, 'w') as f:
                json.dump(default_config, f)
            EMOTE_API_URL = default_config['api_url']
            logger.info("Default API config created")
            return True
        except Exception as e:
            logger.error(f"Error creating API config: {e}")
            return False

def save_api_config(api_url):
    """Save API configuration to JSON file."""
    try:
        config = {'api_url': api_url}
        with open(API_CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        
        global EMOTE_API_URL
        EMOTE_API_URL = api_url
        logger.info(f"API config saved: {api_url}")
        return True
    except Exception as e:
        logger.error(f"Error saving API config: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    chat_type = update.effective_chat.type
    
    # Check if bot is being used in private chat
    if chat_type == "private":
        # Only show API info to owner
        if update.effective_user.id == OWNER_ID:
            current_api = EMOTE_API_URL if EMOTE_API_URL else "Not set"
            await update.message.reply_text(
                f"👋 Hello Owner!\n\n"
                f"🤖 *Bot Status:*\n"
                f"• Current API: `{current_api}`\n"
                f"• Config File: `{API_CONFIG_FILE}`\n\n"
                f"*Owner Commands:*\n"
                f"/addapi <api_url> - Change API URL\n"
                f"/showapi - Show current API (hidden in groups)\n"
                f"/allow <group_id> - Allow group\n"
                f"/remove <group_id> - Remove group\n"
                f"/listgroups - List allowed groups",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ This bot only works in groups!\n\n"
                "Please add me to a group and use commands from there."
            )
        return
    
    await update.message.reply_text(
        f"👋 Hello {user.mention_html()}!\n\n"
        "Welcome to Emote Bot! 🤖\n\n"
        "Available Commands:\n"
        "/help - Show help message\n"
        "/emote - Perform emote with teammates"
        "If You Want More Emote ID's https://ff-item.netlify.app/?p=2&t=emote",
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
🤖 *Emote Bot Help* 🤖

*Available Commands:*

• /start - Start the bot
• /help - Show this help message
• /emote - Perform emote with teammates
• Emote Library= https://ff-item.netlify.app/?p=1&t=emote
*Emote Command Format:*

1️⃣ *Single Player:*
   `/emote 3737648 1561796367 {emote_id}`

2️⃣ *Duo:*
   `/emote 3737648 1561796367 7474838473 {emote_id}`

3️⃣ *Triple:*
   `/emote 3737648 1561796367 7474838473 3036201883 {emote_id}`

4️⃣ *Quad:*
   `/emote 3737648 1561796367 7474838473 838483858 7374829858 {emote_id}`

*Rules:*
• Team code must be exactly 7 digits
• UIDs can vary in length
• Emote ID must be provided

*Example:* `/emote 1234567 111222333 444555666 888999000 909000063`
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def addapi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change API URL (Owner only, works in private chat only)."""
    # Check if user is owner
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only the bot owner can use this command!")
        return
    
    # Check if used in private chat
    chat_type = update.effective_chat.type
    if chat_type != "private":
        await update.message.reply_text(
            "⚠️ For security, this command only works in private chat!\n\n"
            "Please message me privately to change the API."
        )
        return
    
    # Check if API URL is provided
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide an API URL!\n\n"
            "Usage: /addapi https://api.example.com/endpoint\n\n"
            f"Current API: `{EMOTE_API_URL}`",
            parse_mode='Markdown'
        )
        return
    
    api_url = context.args[0].strip()
    
    # Basic URL validation
    if not api_url.startswith(('http://', 'https://')):
        await update.message.reply_text("❌ Invalid URL! Must start with http:// or https://")
        return
    
    # Save to config file
    if save_api_config(api_url):
        await update.message.reply_text(
            f"✅ API updated successfully!\n\n"
            f"New API: `{api_url}`\n"
            f"Config saved to: `{API_CONFIG_FILE}`",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Failed to save API configuration! Check logs for details."
        )

async def showapi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current API URL (Owner only, hidden in groups)."""
    # Check if user is owner
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only the bot owner can use this command!")
        return
    
    chat_type = update.effective_chat.type
    
    if chat_type == "private":
        # Show full API in private chat
        await update.message.reply_text(
            f"🔧 *Current API Configuration:*\n\n"
            f"• API URL: `{EMOTE_API_URL}`\n"
            f"• Config File: `{API_CONFIG_FILE}`\n"
            f"• File Exists: `{os.path.exists(API_CONFIG_FILE)}`",
            parse_mode='Markdown'
        )
    else:
        # In groups, show only status (not the actual URL)
        status = "✅ Configured" if EMOTE_API_URL else "❌ Not set"
        await update.message.reply_text(
            f"🔧 *API Status:* {status}\n\n"
            f"*Note:* API URL is hidden in groups for security.\n"
            f"Use /addapi in private chat to change it.",
            parse_mode='Markdown'
        )

async def emote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the emote command."""
    # Check if API is configured
    if not EMOTE_API_URL:
        await update.message.reply_text(
            "❌ API not configured!\n\n"
            "Bot owner needs to set API URL first using /addapi command."
        )
        return
    
    # Check if enough arguments are provided
    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ Invalid format!\n\n"
            "Minimum format: /emote {team_code} {uid1} {emote_id}\n\n"
            "Use /help to see all formats."
        )
        return
    
    try:
        # Parse arguments
        team_code = context.args[0]
        
        # Validate team code (7 digits)
        if not (team_code.isdigit() and len(team_code) == 7):
            await update.message.reply_text("❌ Team code must be exactly 7 digits!")
            return
        
        # Extract UIDs and emote_id
        # Last argument is emote_id, rest are UIDs
        emote_id = context.args[-1]
        uids = context.args[1:-1]
        
        # Validate we have between 1-4 UIDs
        if not (1 <= len(uids) <= 4):
            await update.message.reply_text("❌ You must provide 1-4 UIDs!")
            return
        
        # Prepare API parameters
        params = {
            'tc': team_code,
            'emote_id': emote_id
        }
        
        # Add UIDs to params
        for i, uid in enumerate(uids, 1):
            params[f'uid{i}'] = uid
        
        # For missing UIDs, send empty string
        for i in range(len(uids) + 1, 5):
            params[f'uid{i}'] = ''
        
        # Call the API
        await update.message.reply_text("🔄 Performing emote... Please wait!")
        
        response = requests.get(EMOTE_API_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                message = f"""
✅ *Emote Successful!* ✅

*Details:*
• Team Code: `{data.get('team_code', team_code)}`
• Emote ID: `{data.get('emote_id', emote_id)}`
• Message: {data.get('message', 'Success')}

*Players UIDs:*
"""
                for uid in data.get('uids', uids):
                    message += f"• `{uid}`\n"
                
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    f"❌ API Error: {data.get('message', 'Unknown error')}"
                )
        else:
            await update.message.reply_text(
                f"❌ Server Error: Status code {response.status_code}"
            )
            
    except requests.exceptions.Timeout:
        await update.message.reply_text("❌ Request timeout! Please try again.")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Network Error: {str(e)}")
    except Exception as e:
        logger.error(f"Error in emote command: {e}")
        await update.message.reply_text("❌ An error occurred! Please check your inputs.")

async def allow_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow a group to use the bot (Owner only)."""
    # Check if user is owner
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only the bot owner can use this command!")
        return
    
    # Check if group ID is provided
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a group ID!\n"
            "Usage: /allow <group_id>"
        )
        return
    
    try:
        group_id = int(context.args[0])
        ALLOWED_GROUPS.add(group_id)
        
        await update.message.reply_text(
            f"✅ Group `{group_id}` has been added to the allowed list!",
            parse_mode='Markdown'
        )
        logger.info(f"Group {group_id} added to allowed list by {update.effective_user.id}")
        
    except ValueError:
        await update.message.reply_text("❌ Invalid group ID! Must be a number.")

async def remove_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a group from allowed list (Owner only)."""
    # Check if user is owner
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only the bot owner can use this command!")
        return
    
    # Check if group ID is provided
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a group ID!\n"
            "Usage: /remove <group_id>"
        )
        return
    
    try:
        group_id = int(context.args[0])
        
        if group_id in ALLOWED_GROUPS:
            ALLOWED_GROUPS.remove(group_id)
            await update.message.reply_text(
                f"✅ Group `{group_id}` has been removed from the allowed list!",
                parse_mode='Markdown'
            )
            logger.info(f"Group {group_id} removed from allowed list by {update.effective_user.id}")
        else:
            await update.message.reply_text(f"❌ Group `{group_id}` is not in the allowed list!")
            
    except ValueError:
        await update.message.reply_text("❌ Invalid group ID! Must be a number.")

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all allowed groups (Owner only)."""
    # Check if user is owner
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only the bot owner can use this command!")
        return
    
    if not ALLOWED_GROUPS:
        await update.message.reply_text("📝 No groups are currently allowed.")
        return
    
    groups_list = "\n".join([f"• `{group_id}`" for group_id in ALLOWED_GROUPS])
    await update.message.reply_text(
        f"📋 *Allowed Groups:*\n\n{groups_list}",
        parse_mode='Markdown'
    )

def main():
    """Start the bot."""
    # Load API configuration
    if not load_api_config():
        print("❌ Failed to load API configuration!")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addapi", addapi))
    application.add_handler(CommandHandler("showapi", showapi))
    application.add_handler(CommandHandler("emote", emote))
    application.add_handler(CommandHandler("allow", allow_group))
    application.add_handler(CommandHandler("remove", remove_group))
    application.add_handler(CommandHandler("listgroups", list_groups))
    
    # Start the Bot
    print("🤖 Bot is starting...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"🔗 Current API: {EMOTE_API_URL}")
    print(f"📁 Config File: {API_CONFIG_FILE}")
    print("📢 Bot is now PUBLIC - Anyone can use in groups!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()