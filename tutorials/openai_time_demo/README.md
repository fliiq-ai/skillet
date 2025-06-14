# OpenAI + Skillet Time Demo

This tutorial demonstrates how to use OpenAI's GPT models to interact with the Skillet time skill. It shows how to:
- Set up function calling with OpenAI
- Make requests to the Skillet time service
- Handle responses and errors gracefully

## Prerequisites

- Python 3.8+
- OpenAI API key
- Running Skillet time service

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create your .env file
cp .env.example .env

# Edit .env with your actual OpenAI API key
# DO NOT commit this file - it's already in .gitignore
```

3. Add your OpenAI API key to the `.env` file:
```bash
OPENAI_API_KEY=your_key_here
```

4. Start the Skillet time service (in another terminal):
```bash
cd examples/anthropic_time
pip install -r requirements.txt
uvicorn skillet_runtime:app --reload
```

## Running the Demo

```bash
python main.py
```

The demo will start an interactive session where you can ask questions about time in different timezones. The OpenAI model will interpret your questions and use the Skillet time service to get accurate answers.

## Example Questions

Try asking:
- "What time is it now?"
- "Tell me the current time in Tokyo"
- "What's the time in New York and London?"
- "Give me the time in Pacific timezone"

## How it Works

1. Your question is sent to OpenAI's API
2. OpenAI interprets the question and calls the appropriate function
3. The function makes a request to the Skillet time service
4. The response is formatted and returned to you

## Error Handling

The demo includes handling for common errors:
- Invalid timezones
- Service connection issues
- API rate limits

## Files

- `main.py` - The main demo application
- `requirements.txt` - Required Python packages
- `README.md` - This documentation
- `.env.example` - Template for environment variables (copy to `.env` and add your API key)

## Security Note

Never commit your `.env` file or expose your API keys. The `.env` file is already included in the root `.gitignore` to prevent accidental commits.
