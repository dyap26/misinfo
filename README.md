# Misinformation App
A mobile app dedicated to reviewing news articles for misinformation using Claude AI.

## Tech Stack
**Framework and Runtime**
* Python 

**AI and Content Processing**
* **Anthropic SDK (v0.84.0)** - Claude API Integration <br>
[NewsAPI](https://newsapi.org/)

## Architecture
### **Agent Implementation**
**Processing Flow:**
1. Content Fetching - Fetches multiple articles based on the inputted keyword(s).
2. Content Extraction - Scrape
3. AI Analysis - Sends the extracted data to Claude for structured analysis and scoring.
4. Ranking 

**Model Configuration:**
* Model: > claude-sonnet-4-6
* Max Tokens Per Article: 800

## Getting Started
1. Install dependencies
```bash
npm install
pip install -r requirements.txt
```
2. Fill Environment Variables <br>
Create a ```bash .env.local``` file with the following variables:
```bash
NEWS_API_KEY = your_news_api_key
ANTHROPIC_API_KEY = your_anthropic_api_key
```
3. Test the Backend <br>
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