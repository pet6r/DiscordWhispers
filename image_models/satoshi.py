"""
    Discord bot for analyzing images using the Ollama API, providing intelligent responses based on the image content.

    The bot listens for image attachments in Discord messages, processes the image using a local LLM API, and replies
    with an analysis of the image. The bot can be triggered either by mentioning the bot directly or by specific phrases.

    Args:
        image (PIL.Image): The image attached in the Discord message.
        question (str): The prompt or question asked about the image (e.g., "What is in the image?").

    Environment Variables:
        SATOSHI_TOKEN (str): The Discord bot token to authenticate and run the bot.

    API Integration:
        - Ollama API for image understanding and text generation.
        - Converts image to base64 format before sending it to the API.
        - Sends a POST request to the API's /generate endpoint with the image and prompt.

    Discord Events:
        - on_ready(): Prints when the bot is connected and in how many guilds.
        - on_message(message): Processes the message content and checks for attachments to analyze.

    Example Usage:
        1. Mention the bot (@satoshi) in a message and attach an image. The bot will reply with an analysis of the image.
        2. Use the `!satoshi` command to prompt the bot for further image analysis instructions.

    Returns:
        str: The response from the Ollama API, either analyzing the image or returning an error message.
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import requests
from io import BytesIO
from PIL import Image
import base64
import json

# Load environment variables (e.g., for the bot token)
load_dotenv()

import sys

# Set Windows-specific event loop policy for compatibility with asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Set up Discord bot intents to allow message content processing
intents = discord.Intents.default()
intents.message_content = True

# Create the bot instance with a command prefix
satoshi = commands.Bot(command_prefix="!", intents=intents)

# Function to process images and text using the Ollama API
# This function sends the image and the question (prompt) to an LLM model
async def ask_about_image_via_generate(image, question):
    try:
        # Convert the image into base64 format for API transmission
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Construct the payload for the API request with the image and question
        payload = {
            "model": "llava-llama3:latest",  # Specify the model used for image understanding
            "prompt": question,
            "images": [img_str],  # Send the base64-encoded image as an array
            "stream": False  # Streaming is disabled for simplicity
        }

        # Send the payload to the local Ollama generate API endpoint
        response = requests.post(
            'http://localhost:11434/api/generate',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )

        # If the API response is successful, extract the result
        if response.status_code == 200:
            result = response.json()
            return result.get('response', "I couldn't understand the image.")
        else:
            # Return an error message if the API call fails
            return f"Error: {response.status_code} - {response.text}"

    except Exception as e:
        # Handle exceptions during image processing
        print(f"Error in ask_about_image_via_generate: {e}")
        return "I'm sorry, I couldn't process the image."

# Function to fetch an image from a given URL (attachment)
async def fetch_image_from_url(url):
    try:
        # Send an HTTP GET request to fetch the image
        response = requests.get(url)
        # Convert the response content to an image (RGB format)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        return img
    except Exception as e:
        # Handle exceptions in case the image fetch fails
        print(f"Error fetching image: {e}")
        return None

# Event that triggers when the bot successfully connects to Discord
@satoshi.event
async def on_ready():
    print(f"{satoshi.user} has connected to Discord.")
    # Output the number of guilds (servers) the bot is connected to
    print(f"Bot is in {len(satoshi.guilds)} guild(s).")
    # List each guild's name and ID for reference
    for guild in satoshi.guilds:
        print(f" - {guild.name} (id: {guild.id})")

# Event that handles incoming messages
@satoshi.event
async def on_message(message):
    # Prevent the bot from responding to its own messages
    if message.author == satoshi.user:
        return

    # Allow the bot to process commands from the message
    await satoshi.process_commands(message)

    # Check if the bot is mentioned directly or "hello satoshi" is mentioned
    if satoshi.user in message.mentions or 'hello satoshi' in message.content.lower():
        # Clean up the prompt by removing mentions or trigger phrases
        prompt = message.content.replace(f'<@!{satoshi.user.id}>', '').replace(f'<@{satoshi.user.id}>', '')
        prompt = prompt.replace('hello satoshi', '', 1).trim()

        # Set a default question if no specific question is provided
        if not prompt:
            prompt = "What is in the image?"

        # If the message has an image attachment, proceed with image analysis
        if message.attachments:
            image_url = message.attachments[0].url
            image = await fetch_image_from_url(image_url)

            if image:
                # Indicate that the bot is processing the image
                async with message.channel.typing():
                    # Debugging log for prompt and image processing
                    print(f"Processing image with prompt: {prompt}")
                    # Send the image and prompt to the LLM API and get a response
                    response = await ask_about_image_via_generate(image, prompt)
                    # Send the response back to the Discord channel
                    await message.channel.send(response)
            else:
                # Send an error message if the image couldn't be fetched
                await message.channel.send("I couldn't fetch the image.")
        else:
            # Prompt the user to attach an image if none was provided
            await message.channel.send("Please attach an image for me to analyze.")

# Command to handle direct interactions with the bot
# This command prompts users to upload an image for analysis
@satoshi.command(name="satoshi")
async def chat(ctx, *, prompt):
    # Send a message instructing the user to upload an image
    await ctx.send("Please attach an image for me to analyze.")

# Entry point of the bot script
if __name__ == "__main__":
    # Retrieve the bot token from the environment variables
    satoshi_token = os.getenv("SATOSHI_TOKEN")
    # Run the bot using the retrieved token
    satoshi.run(satoshi_token)
1 