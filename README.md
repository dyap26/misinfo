# Misinformation App

A mobile app dedicated to reviewing news articles for misinformation using Claude AI. Built with Expo, TypeScript, and Python.

## Tech Stack

**Backend**
- Python — core runtime
- FastAPI + Uvicorn — REST API server
- Anthropic SDK — Claude API integration for credibility scoring
- NewsAPI — article discovery and fetching
- newspaper3k + httpx — article scraping and text extraction

**Frontend**
- React Native (Expo SDK 54) — mobile application
- React Navigation — screen routing
- react-native-svg — score visualizations

## Architecture

### **Agent Implementation**

**Processing Flow:**
1. Content Fetching - Fetches multiple articles based on the inputted keyword(s).
2. Content Extraction - Scrape text from each article.
3. AI Analysis - Sends the extracted data to Claude for structured analysis and scoring.
4. Ranking 

**Model Configuration:**
* Model: `claude-sonnet-4-6`
* Max Tokens Per Article: 800

## Scoring

Articles are scored based off of 7 factors and their respective weighting: <br>
1. Evidence Quality:     (22%)
2. Verifiability:        (18%)
3. Factual Language:     (15%)
4. Logical Consistency:  (15%)
5. Context and Framing:  (15%)
6. Balance:              (10%)
7. Source Reputation:    (5%)

## Project Structure

```
backend/
├── fetch_articles.py          # Article fetch
├── main.py                    # Main testpoint
├── pipeline.py                # Main pipeline
├── scorer.py                  # AI scorer
├── scraper.py                 # Article scraper
frontend/
├── app/                       # Application screens
├── components/                # Reusable UI components
├── constants/                 # App-wide constants
├── hooks/                     # Custom React hooks
├── types/                     # TypeScript type definitions
└── App.tsx                    # Main application entry point
```

## Getting Started

1. Install Node.js and npm
    * Download from [nodejs.org](https://nodejs.org/)
    * Or use a package manager:
        * macOS: `brew install node`
        * Windows: Use the installer from nodejs.org
        * Linux: `sudo apt install nodejs npm`
2. Install Expo CLI globally
    ```bash
    npm install -g expo-cli
    ```
3. Install dependencies
    ```bash
    npm install
    pip install -r requirements.txt
    ```
4. Fill Environment Variables <br>
    There are two .env.local files needed.
    Create a ```bash .env.local``` file in the backend folder with the following variables:
    ```bash
    NEWS_API_KEY = your_news_api_key
    ANTHROPIC_API_KEY = your_anthropic_api_key
    ```
    Create a ```bash .env.local``` file in the frontend folder with the following variables:
    ```bash
    EXPO_PUBLIC_API_BASE_URL = your_backend_url # e.g. http://192.168.x.x:8000
    ```
5. Test the Backend <br>
    There are three different ways to test the backend from the terminal:
    * Singular keyword
    ``` bash
    python3 main.py your_keyword
    ```
    * Multiple keywords
    ``` bash
    python3 main.py keyword_1 keyword_2 keyword_3
    ```
6. Start Development Server <br>
    To test locally, you will need two terminal tabs open
    * Backend
    ``` bash
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    * Frontend
    ``` bash
    cd frontend
    npx expo start
    ```
## Contributing

Contributions are welcome. Feel free to submit a pull request.

## Acknowledgements

I'll fill this out later
