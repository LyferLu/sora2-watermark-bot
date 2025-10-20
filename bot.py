
import logging
import os
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration ---
# Get bot token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set.")
    exit(1)

# Watermark image path (assuming it's in the same directory)
WATERMARK_PATH = 'sora_logo.png'

# --- Helper Functions ---
async def add_watermark_to_video(video_path: str, output_path: str, watermark_path: str):
    try:
        video = VideoFileClip(video_path)

        # Resize watermark image to fit video (e.g., 10% of video width)
        watermark_original = Image.open(watermark_path)
        video_width, video_height = video.size
        
        # Calculate watermark size (e.g., 15% of video width)
        watermark_width = int(video_width * 0.15)
        watermark_height = int(watermark_original.height * (watermark_width / watermark_original.width))

        # Ensure watermark has an alpha channel for transparency
        if watermark_original.mode != 'RGBA':
            watermark_original = watermark_original.convert('RGBA')
        
        watermark_resized = watermark_original.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
        watermark_resized.save('temp_watermark.png') # Save resized watermark temporarily

        watermark = ImageClip('temp_watermark.png', duration=video.duration)
        
        # Position watermark (e.g., bottom-right corner with some padding)
        padding = int(video_width * 0.02) # 2% padding
        x_position = video_width - watermark.w - padding
        y_position = video_height - watermark.h - padding

        final_video = CompositeVideoClip([video, watermark.set_pos((x_position, y_position))])
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

        # Clean up temporary watermark file
        os.remove('temp_watermark.png')
        
        return True
    except Exception as e:
        logger.error(f"Error adding watermark: {e}")
        return False
    finally:
        if 'video' in locals() and video:
            video.close()
        if 'final_video' in locals() and final_video:
            final_video.close()

# --- Telegram Bot Handlers ---
async def start(update: Update, context) -> None:
    await update.message.reply_text(
        'Привет! Отправь мне видео, и я добавлю на него водяной знак Sora2.'
    )

async def handle_video(update: Update, context) -> None:
    user = update.message.from_user
    logger.info(f"User {user.first_name} sent a video.")
    
    await update.message.reply_text("Получил видео. Обрабатываю... Это может занять некоторое время.")

    video_file = await update.message.video.get_file()
    input_video_path = f"downloads/{video_file.file_id}.mp4"
    output_video_path = f"processed/{video_file.file_id}_watermarked.mp4"

    os.makedirs('downloads', exist_ok=True)
    os.makedirs('processed', exist_ok=True)

    try:
        await video_file.download_to_drive(input_video_path)
        logger.info(f"Video downloaded to {input_video_path}")

        if await add_watermark_to_video(input_video_path, output_video_path, WATERMARK_PATH):
            logger.info(f"Watermark added. Sending {output_video_path}")
            await update.message.reply_video(video=open(output_video_path, 'rb'))
            await update.message.reply_text("Ваше видео с водяным знаком готово!")
        else:
            await update.message.reply_text("Произошла ошибка при добавлении водяного знака.")

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await update.message.reply_text("Произошла непредвиденная ошибка при обработке вашего видео.")
    finally:
        # Clean up files
        if os.path.exists(input_video_path):
            os.remove(input_video_path)
        if os.path.exists(output_video_path):
            os.remove(output_video_path)
        logger.info("Cleaned up temporary files.")

async def error_handler(update: Update, context) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update.effective_message:
        await update.effective_message.reply_text("Извините, произошла ошибка. Пожалуйста, попробуйте еще раз.")

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO & ~filters.COMMAND, handle_video))
    application.add_error_handler(error_handler)

    logger.info("Bot started polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

