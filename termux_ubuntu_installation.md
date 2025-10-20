# Termux Ubuntu Installation Guide

This guide provides step-by-step instructions to install Ubuntu on Termux using the `jorexdeveloper/termux-ubuntu` script, as well as general Termux setup. This setup will be used to host the Sora2 watermark Telegram bot.

## Prerequisites

*   An Android device with Termux installed. You can download Termux from F-Droid or the Google Play Store.
*   A stable internet connection.
*   Sufficient storage space on your Android device.

## Step 1: Update Termux Packages

First, open Termux and update all existing packages to their latest versions.

```bash
pkg update && pkg upgrade -y
```

## Step 2: Install Essential Packages

Install necessary tools like `wget`, `proot`, and `git` which are required for downloading and setting up Ubuntu.

```bash
pkg install wget proot git -y
```

## Step 3: Clone the Termux Ubuntu Repository

Navigate to your home directory and clone the `jorexdeveloper/termux-ubuntu` repository.

```bash
cd ~/
git clone https://github.com/jorexdeveloper/termux-ubuntu.git
```

## Step 4: Install Ubuntu

Change into the cloned directory and run the installation script. This script will download and set up the Ubuntu file system.

```bash
cd termux-ubuntu
chmod +x ubuntu.sh
./ubuntu.sh
```

Follow any on-screen prompts during the installation process.

## Step 5: Start Ubuntu

Once the installation is complete, you can start your Ubuntu environment by running:

```bash
./start-ubuntu.sh
```

To exit the Ubuntu environment and return to Termux, type `exit`.

## Step 6: Initial Ubuntu Setup (Inside Ubuntu Environment)

After entering the Ubuntu environment, it's good practice to update its package lists.

```bash
apt update && apt upgrade -y
```

## Step 7: Python 3.11 and venv Setup

Since the bot requires Python 3.11 and a `venv` environment named `ai`, you'll need to ensure these are set up within your Ubuntu environment.

### Install Python 3.11 (if not already present)

Ubuntu 22.04 (which is likely installed by the script) typically comes with Python 3.10 or newer. You can check your Python version:

```bash
python3 --version
```

If Python 3.11 is not the default, you might need to install it. First, ensure you have `software-properties-common` to add repositories:

```bash
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install python3.11 python3.11-venv -y
```

### Create and Activate Virtual Environment

Once Python 3.11 is available, create your virtual environment named `ai`:

```bash
mkdir ~/ai
cd ~/ai
python3.11 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefixing your prompt, indicating the virtual environment is active.

## Troubleshooting

*   **Permissions Denied**: Ensure you have executed `chmod +x ubuntu.sh` before running the script.
*   **Internet Issues**: Check your device's internet connection if downloads fail.
*   **Storage Space**: Make sure you have enough free storage on your device for the Ubuntu installation.

This document will be part of the new repository for the Sora2 watermark bot. The next steps will involve developing the bot and documenting its setup and usage within this environment.
