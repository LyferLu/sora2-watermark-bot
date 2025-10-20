# Sora2 Watermark Telegram Bot

This Telegram bot automatically adds a Sora2 watermark to videos sent by users. It's designed to be easily deployable, including on Termux Ubuntu environments.

## Features

*   **Start Command**: Responds to `/start` with a welcome message.
*   **Video Watermarking**: Automatically detects video messages, downloads them, adds a Sora2 watermark, and sends the processed video back to the user.
*   **Error Handling**: Provides user-friendly error messages for processing failures.
*   **Clean-up**: Removes temporary video files after processing.

## Prerequisites

Before you begin, ensure you have:

*   A Telegram Bot Token from BotFather. If you don't have one, create a new bot by talking to [@BotFather](https://t.me/BotFather) on Telegram and obtaining your API token.
*   A system capable of running Python 3.11 with `pip` and `ffmpeg` installed. This guide specifically covers setup on Termux Ubuntu.

## Setup and Installation

This section details how to set up and run the bot. If you are setting this up on an Android device using Termux, please follow the [Termux Ubuntu Installation Guide](termux_ubuntu_installation.md) first to prepare your environment.

### 1. Prepare your Environment

If you are using Termux on Android, first follow the instructions in [Termux Ubuntu Installation Guide](termux_ubuntu_installation.md) to set up your Ubuntu environment and Python 3.11 virtual environment. Ensure your virtual environment (`ai`) is activated.

For other Linux-based systems, ensure Python 3.11 is installed and create a virtual environment:

```bash
python3.11 -m venv ai
source ai/bin/activate
```

### 2. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/Error404rt/sora2-watermark-bot.git
cd sora2-watermark-bot
```

### 3. Install Dependencies

With your virtual environment activated, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg

The `moviepy` library used for video processing relies on `ffmpeg`. You need to install it separately.

**On Ubuntu/Debian-based systems (including Termux Ubuntu):**

```bash
sudo apt update
sudo apt install ffmpeg -y
```

**On other systems**, please refer to the `ffmpeg` official documentation for installation instructions.

### 5. Configure Telegram Bot Token

Create a file named `.env` in the root directory of the bot (where `bot.py` is located) and add your Telegram Bot Token:

```
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
```

Replace `YOUR_TELEGRAM_BOT_TOKEN_HERE` with the actual token you obtained from BotFather.

### 6. Run the Bot

Ensure your virtual environment is active and then run the bot script:

```bash
python bot.py
```

The bot will start polling for updates. You can now interact with it on Telegram.

## Bot Usage

1.  **Start the Bot**: Send the `/start` command to your bot on Telegram.
2.  **Send a Video**: Send any video file to the bot.
3.  **Receive Watermarked Video**: The bot will process your video, add the Sora2 watermark, and send it back to you.

## Watermark Details

The Sora2 watermark (`sora_logo.png`) is placed in the bottom-right corner of the video with a slight padding. The size of the watermark is dynamically adjusted to be 15% of the video's width, maintaining its aspect ratio.

## Troubleshooting

*   **`TELEGRAM_BOT_TOKEN` not found**: Make sure you have created the `.env` file and set the `TELEGRAM_BOT_TOKEN` correctly.
*   **`ffmpeg` not found**: Ensure `ffmpeg` is installed and accessible in your system's PATH.
*   **Video processing errors**: Check the bot's logs for specific error messages. Ensure the video file is not corrupted and is in a format `moviepy` can handle.
*   **Virtual Environment**: Always ensure your `ai` virtual environment is activated before installing dependencies or running the bot.

## Contributing

Feel free to fork the repository, make improvements, and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details. (Note: A `LICENSE` file will be added in a future update if required.)
