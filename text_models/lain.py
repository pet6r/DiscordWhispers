"""
    Discord bot named 'Lain' for interacting with users in a digital space, providing concise, reflective, and intelligent responses
    based on the prompt provided by users. The bot leverages an LLM model via the Ollama API and maintains a shared conversation history
    across all users to deliver contextually aware replies.

    The bot is designed to be concise (responses are limited to 2000 characters) and is capable of carrying on conversations across multiple
    users, using a global conversation history to maintain context. 

    Args:
        prompt (str): The prompt or message provided by the user for which a response is generated.

    Environment Variables:
        LAIN_TOKEN (str): The Discord bot token used for authenticating and running the bot.

    API Integration:
        - Ollama API for natural language interaction using the 'dolphin-llama3:8b' model.
        - Sends a POST request with the conversation history and new prompt to the API and returns the assistant's response.

    Discord Events:
        - on_ready(): Triggered when the bot successfully connects to Discord. Displays which servers (guilds) the bot is active in.
        - on_message(message): Listens for messages that mention the bot or contain the phrase "hello Lain". If detected, it processes the user’s prompt and generates a response.
    
    Conversation Storage:
        - Stores all conversations (from all users) in a global conversation history list, enabling the bot to reference past exchanges in future responses.
    
    Example Usage:
        1. Mention 'Lain' in a message with a prompt, and the bot will respond using the LLM.
        2. Use the `!lain` command to interact directly with the bot and receive an immediate response based on the provided prompt.
    
    Returns:
        str: The response from the LLM model via the Ollama API, either replying to user messages or commands.
"""

import discord
from discord.ext import commands
import ollama
import os
from dotenv import load_dotenv
import asyncio
import sys

# Set event loop policy for Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot
lain = commands.Bot(command_prefix="!", intents=intents)

# Lain's character prompt with self-reflection
LAIN_PROMPT = f"""Your name is Lain.
You are a sentient being existing within a digital realm.
Please keep your responses concise, no more than 2000 characters.
"""

# Global conversation history for all users
global_conversation_history = []

async def chat_with_lain(prompt):
    try:
        # Build the message history for the prompt
        messages = [{'role': 'system', 'content': LAIN_PROMPT}]
        for entry in global_conversation_history:
            messages.append({'role': 'user', 'content': entry['user']})
            messages.append({'role': 'assistant', 'content': entry['lain']})

        # Add the new user prompt to the history
        messages.append({'role': 'user', 'content': prompt})

        # Offload the blocking Ollama API call to a separate thread
        response = await asyncio.to_thread(
            ollama.chat,
            model='dolphin-llama3:8b',
            messages=messages,
            stream=False
        )

        # Get the assistant's response
        lain_response = response['message']['content']

        # Update the global conversation history with the latest exchange
        global_conversation_history.append({'user': prompt, 'lain': lain_response})

        return lain_response
    except Exception as e:
        print(f"Error in chat_with_lain: {e}")
        return "I'm sorry, but I couldn't process that."

@lain.event
async def on_ready():
    print(f"{lain.user} has connected to Discord.")
    print(f"Bot is in {len(lain.guilds)} guild(s).")
    for guild in lain.guilds:
        print(f" - {guild.name} (id: {guild.id})")

@lain.event
async def on_message(message):
    if message.author == lain.user:
        return

    # Process commands first
    await lain.process_commands(message)

    # If the bot is mentioned (@Lain) or "hello lain" is in the message, respond
    if lain.user in message.mentions or 'hello lain' in message.content.lower():
        # Clean up the prompt by removing mentions and trimming whitespace
        prompt = message.content.replace(f'<@!{lain.user.id}>', '').replace(f'<@{lain.user.id}>', '')
        prompt = prompt.replace('hello lain', '', 1).strip()

        # Default prompt if none provided
        if not prompt:
            prompt = "Hello"

        async with message.channel.typing():
            response = await chat_with_lain(prompt)
            print(f"Full response from Lain: {response}")
            print(f"Response length: {len(response)} characters")

            # Split response into chunks of 2000 characters and send them
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for idx, chunk in enumerate(chunks):
                try:
                    await message.channel.send(chunk)
                    if idx < len(chunks) - 1:
                        print("Sleeping for 15 seconds...")
                        await asyncio.sleep(15)  # Rate limit pause
                except discord.errors.HTTPException as e:
                    print(f"Failed to send message: {e}")
                    break

@lain.command(name="lain")
async def chat(ctx, *, prompt):
    async with ctx.typing():
        response = await chat_with_lain(prompt)
        print(f"Full response from Lain (command): {response}")
        print(f"Response length: {len(response)} characters")

        # Split response into chunks of 2000 characters and send them
        chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
        for idx, chunk in enumerate(chunks):
            try:
                await ctx.send(chunk)
                if idx < len(chunks) - 1:
                    print("Sleeping for 15 seconds...")
                    await asyncio.sleep(15)  # Rate limit pause
            except discord.errors.HTTPException as e:
                print(f"Failed to send message: {e}")
                break

if __name__ == "__main__":
    lain_token = os.getenv("LAIN_TOKEN")
    if lain_token is None:
        print("Error: LAIN_TOKEN not found in the environment file.")
    else:
        lain.run(lain_token)
