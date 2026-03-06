# Misinformation App

A mobile app dedicated to reviewing news articles for misinformation using Claude AI.

## Tech Stack
Claude
[NewsAPI](https://newsapi.org/)

## Getting Started
1. Install dependencies
```bash
npm install
pip install -r requirements.txt
```
2. Fill Environment Variables
## Environment Variables
Create a ```bash .env.local``` file with the following variables:
```bash
NEWS_API_KEY = your_news_api_key
ANTHROPIC_API_KEY = your_anthropic_api_key
```
3. Test the Backend
There are three different ways to test the backend from the terminal:
* Singular keyword
``` bash
python3 main.py your_keyword
```
* Multiple keywords
``` bash
python3 main.py keyword_1 keyword_2 keyword_3
```

## Acknowledgements
I'll fill this out later