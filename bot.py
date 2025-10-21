
import logging
import os
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from moviepy.editor import VideoFileClip, CompositeVideoClip
import moviepy.video.fx.all as vfx

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
WATERMARK_PATH = 'sorawatermark.mp4'

# --- Helper Functions ---
async def add_watermark_to_video(video_path: str, output_path: str, watermark_path: str,
                                 opacity=0.7, scale=0.14):
    """
    在主视频上添加一个移动的 MP4 视频水印。

    :param video_path: 主视频文件路径。
    :param watermark_path: 作为水印的 MP4 视频文件路径。
    :param output_path: 输出视频文件路径。
    :param opacity: 水印的不透明度 (0.0 到 1.0)。
    :param scale: 水印相对于主视频尺寸的缩放比例。
    """
    try:
        # 1. 加载主视频和水印视频
        clip = VideoFileClip(video_path)
        watermark = VideoFileClip(watermark_path)
        duration = clip.duration

        # 2. 获取水印的 *原始* 时长，这将作为我们的“变换周期”
        watermark_duration = watermark.duration
        # 安全检查，防止水印时长为0导致除零错误
        if watermark_duration == 0:
            watermark_duration = duration # 如果水印没时长，就用主视频时长

        # 3. 处理水印视频
        #    - 移除音频以防冲突
        #    - 循环播放，使其总时长与主视频匹配
        watermark = watermark.without_audio().fx(vfx.loop, duration=duration)

        #    - 将视频的“亮度”转换为“不透明度”
        mask = watermark.to_mask()
        watermark = watermark.set_mask(mask)
        #    - 调整尺寸
        watermark = watermark.resize(width=max(clip.w * scale, clip.h * scale, (clip.w + clip.h) * scale*0.75))
        #    - 设置不透明度
        watermark = watermark.set_opacity(opacity)

        # 4. 定义水印出现的位置
        positions = [
            ("left", "top"), 
            ("right", "center"), 
            ("left", "bottom")
        ]
        positions_count = len(positions)

        # 5. 定义一个函数，根据时间 t 返回水印的位置
        def position_at_time(t):
            # 计算当前时间 t 处于第几个 "水印周期"
            #    (t // watermark_duration) 会得到 0, 1, 2, 3...
            current_cycle = int(t // watermark_duration)
            
            # 使用 "模" 运算 (%) 来获取在 positions 中的循环索引
            #    0 % 3 = 0
            #    1 % 3 = 1
            #    2 % 3 = 2
            #    3 % 3 = 0  <-- 开始循环
            #    4 % 3 = 1
            idx = current_cycle % positions_count
            
            x_pos, y_pos = positions[idx]
            # margin = 20  # 离边缘的距离
            margin = min(clip.w, clip.h) * (scale / 4)

            # 计算 x 坐标
            if x_pos == "left":
                px = margin
            elif x_pos == "center":
                px = (clip.w - watermark.w) / 2
            else:  # right
                px = clip.w - watermark.w - margin

            # 计算 y 坐标
            if y_pos == "top":
                py = margin
            elif y_pos == "center":
                py = (clip.h - watermark.h) / 2
            else:  # bottom
                py = clip.h - watermark.h - margin

            return (px, py)

        # 6. 应用动态位置
        watermark = watermark.set_position(lambda t: position_at_time(t))

        # 7. 合成主视频和水印
        final = CompositeVideoClip([clip, watermark])
        
        # 8. 写入最终文件
        final.write_videofile(output_path, codec="libx264", audio_codec="aac", preset="medium")

        
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

