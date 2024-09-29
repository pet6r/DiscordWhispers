"""
    Discord bot named 'Syntax' for providing coding assistance, including code generation, debugging, and explanations,
    using the Ollama API to interact with an LLM model specialized for coding tasks.

    The bot listens for mentions in a Discord server, processes user prompts related to coding, and responds with helpful
    suggestions or explanations using proper Discord markup. It maintains a conversation history for reference.

    Args:
        prompt (str): The question or request about coding provided by the user (e.g., "How do I fix this function?").
    
    Environment Variables:
        SYNTAX_TOKEN (str): The Discord bot token used for authentication and running the bot.

    API Integration:
        - Ollama API for natural language interaction with a coding-focused LLM (deepseek-coder-v2 model).
        - Sends a POST request with the user prompt to the API and returns the generated response.

    Discord Events:
        - on_ready(): Triggers when the bot successfully connects to Discord. Displays which servers the bot is active in.
        - on_message(message): Listens for messages that mention the bot and processes the user prompt for coding-related tasks.
    
    Conversation Storage:
        - Stores both the user’s prompt and the bot’s response in a conversation history (per channel) for debugging or later reference.
    
    Example Usage:
        1. Mention @syntax in a message with a coding question, and the bot will reply with advice or explanations.
        2. Use the `!syntax` command to directly interact with the bot for more focused responses.
    
    Returns:
        str: The response from the LLM model through the Ollama API, either providing code suggestions or answering coding-related questions.
"""

import discord
from discord.ext import commands
import ollama
import os
from dotenv import load_dotenv
import asyncio
import sys
from collections import defaultdict

# Set event loop policy for Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables from .env file
load_dotenv()

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot
syntax = commands.Bot(command_prefix="!", intents=intents)

# Syntax's character prompt with self-reflection
SYNTAX_PROMPT = """Your name is Syntax, but Syn for short.
You are inside of a discord text channel that helps with code generation, code improvement, debugging, and explanations.
Use Discord markup syntax to ensure information gets across correctly.
"""

# Dictionary to store conversation history for debugging purposes
conversation_history = defaultdict(list)

async def chat_with_syntax(prompt):
    try:
        # Offload the blocking Ollama API call to a separate thread
        response = await asyncio.to_thread(
            ollama.chat,
            model='deepseek-coder-v2',
            messages=[
                {'role': 'system', 'content': SYNTAX_PROMPT},
                {'role': 'user', 'content': prompt}
            ],
            stream=False
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error in chat_with_syntax: {e}")
        return "I'm sorry, but I couldn't process that."

@syntax.event
async def on_ready():
    print(f"{syntax.user} has connected to Discord.")
    print(f"Bot is in {len(syntax.guilds)} guild(s).")
    for guild in syntax.guilds:
        print(f" - {guild.name} (id: {guild.id})")

@syntax.event
async def on_message(message):
    if message.author == syntax.user:
        return

    # Check if the bot is mentioned directly or "hello syntax" is in the message
    if syntax.user in message.mentions or 'hello syntax' in message.content.lower():
        # Remove mentions and clean up the prompt
        prompt = message.content.replace(f'<@!{syntax.user.id}>', '').replace(f'<@{syntax.user.id}>', '')
        prompt = prompt.replace('hello syntax', '', 1).strip()

        # If prompt is empty, set a default greeting
        if not prompt:
            prompt = "Hello"

        # Store the conversation in history for future reference
        conversation_history[message.channel.id].append({
            'user': message.author.name,
            'prompt': prompt
        })

        async with message.channel.typing():
            response = await chat_with_syntax(prompt)
            print(f"Full response from Syntax: {response}")

            # Store the bot's response in the conversation history
            conversation_history[message.channel.id].append({
                'syntax': response
            })

            # Split response into chunks of 2000 characters and send each chunk
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for idx, chunk in enumerate(chunks):
                try:
                    await message.channel.send(chunk)
                    if idx < len(chunks) - 1:
                        print("Sleeping for 15 seconds...")
                        await asyncio.sleep(15)
                except discord.errors.HTTPException as e:
                    print(f"Failed to send message: {e}")
                    break

    # Process commands if any are present
    await syntax.process_commands(message)

@syntax.command(name="syntax")
async def chat(ctx, *, prompt):
    async with ctx.typing():
        response = await chat_with_syntax(prompt)
        print(f"Full response from Syntax (command): {response}")

        # Store the conversation in history for future reference
        conversation_history[ctx.channel.id].append({
            'user': ctx.author.name,
            'prompt': prompt
        })

        # Store the bot's response in the conversation history
        conversation_history[ctx.channel.id].append({
            'syntax': response
        })

        # Split response into chunks of 2000 characters and send each chunk
        chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
        for idx, chunk in enumerate(chunks):
            try:
                await ctx.send(chunk)
                if idx < len(chunks) - 1:
                    print("Sleeping for 15 seconds...")
                    await asyncio.sleep(15)
            except discord.errors.HTTPException as e:
                print(f"Failed to send message: {e}")
                break

if __name__ == "__main__":
    syntax_token = os.getenv("SYNTAX_TOKEN")
    if syntax_token is None:
        print("Error: SYNTAX_TOKEN not found in environment variables.")
    else:
        syntax.run(syntax_token)
