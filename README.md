# DiscordWhispers

This repository contains three distinct Discord bots, each utilizing large language models (LLMs) for different purposes: **Syntax**, **Satoshi**, and **Lain**. Each bot provides unique functionalities, from coding assistance to image analysis and conversational interactions.

## Bots Overview:
- **Syntax**: A bot designed to assist with code generation, code improvement, debugging, and explanations using a coding-focused LLM model.
- **Satoshi**: A bot designed for image analysis, allowing users to upload images for detailed LLM-powered insights.
- **Lain**: A conversational bot designed for reflective interactions, leveraging an LLM model to respond intelligently to user prompts.

## Requirements:
- Python 3.8+
- Discord bot tokens for each respective bot
- An active Ollama API running locally 
  
## Installation:
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/pet6r/DiscordWhispers.git
   cd DiscordWhispers
   ```

2. **Install Dependencies**:
   Install all dependencies required for running any of the three bots:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Each bot requires its own Discord bot token to run. You will need to create a `.env` file and add your tokens. Use the following template:
   
   ```bash
   # For running Syntax:
   SYNTAX_TOKEN=your-syntax-bot-token
   
   # For running Satoshi:
   SATOSHI_TOKEN=your-satoshi-bot-token
   
   # For running Lain:
   LAIN_TOKEN=your-lain-bot-token
   ```

4. **Running the Bots**:
   - **Syntax**: A bot for assisting with code-related tasks:
     ```bash
     python syntax.py
     ```
   - **Satoshi**: A bot that analyzes images uploaded to Discord:
     ```bash
     python satoshi.py
     ```
   - **Lain**: A conversational bot designed for reflective interactions:
     ```bash
     python lain.py
     ```

## Customization:
- **Changing the LLM Model**: Each bot uses a different LLM model by default (e.g., `deepseek-coder-v2` for Syntax, `dolphin-llama3:8b` for Lain). You can update and change  the models used by editing the `chat_with_*` function inside each bot's script.

## Usage Examples:
1. **Syntax**:
    Mention `@Syntax` in a message for coding-related questions:
     ```text
     @syntax can you help me write a Python function?
     ```

2. **Satoshi**:
    Upload an image and mention `@Satoshi` to receive insights:
     ```text
     @Satoshi what do you see in this image?
     ```

3. **Lain**:
    Mention `@Lain` for a reflective, concise conversation:
     ```text
     @Lain what is the meaning of life?
     ```

