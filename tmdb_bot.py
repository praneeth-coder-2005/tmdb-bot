import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Bot token and TMDb API key
BOT_TOKEN = "5995472653:AAGCCtCdurJQMOw9Z8DJCFQZG0u2Xg737vY"
TMDB_API_KEY = "bb5f40c5be4b24660cbdc20c2409835e"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the TMDb Search Bot! Send me a movie name, and I'll fetch details for you."
    )

# Search movie function
def search_movie(query):
    url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    return []

# Message	handler for movie search
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    results = search_movie(query)

    if not results:
        await update.message.reply_text("No movies found. Try another search term!")
        return

    # Get the first result
    movie = results[0]
    title = movie.get("title", "N/A")
    overview = movie.get("overview", "No overview available.")
    release_date = movie.get("release_date", "N/A")
    poster_path = movie.get("poster_path")

    # Prepare response
    response = f"**{title}**\n\nRelease Date: {release_date}\n\nOverview: {overview}"

    # Send poster if available
    if poster_path:
        poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}"
        await update.message.reply_photo(photo=poster_url, caption=response, parse_mode="Markdown")
    else:
        await update.message.reply_text(response, parse_mode="Markdown")

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Update {update} caused error {context.error}")
    await update.message.reply_text("Something went wrong. Please try again!")

def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error)

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
