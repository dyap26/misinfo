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
    cd frontend
    npm install
    ```
    ```bash
    cd backend
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
    There are a couple different ways to test the backend from the terminal. First is by just using a keyword/phrase :
    * Keyword/Keyphrase
        ``` bash
        python3 main.py your_keyword
        ```
    By default, the backend will attempt to query a maximum of 5 articles from the ```bash everything``` category. However, you can change these parameters with specific flags:
    * Search within a certain category
        ``` bash
        python3 main.py your_keyword --category your_category
        ```
    * Change maximum number of articles fecthed
        ``` bash
        python3 main.py your_keyword --num-articles num_articles
        ```

    Categories include: <br>
    * business
    * entertainment
    * general
    * health
    * science
    * sports
    * technology

6. Start Development Server <br>
    To test the whole app locally, you will need two terminal tabs open
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

7. Run on device or simulator <br>
    * Scan the QR code with your phone's camera (iOS) or the Expo Go app (Android)
    * Press 'i' for iOS simulator
    * Press 'a' for Android emulator
    * Press 'w' for web browser

## Some Limitations
* The scorer may not analyze and score an article correctly as the NewsAPI might fetch articles that are paywalled or have bot detection.
* Claude may not have the most up-to-date information to cross-reference facts in articles.
* Claude in general :(

## Contributing

Contributions are always welcome! Feel free to submit a pull request.

## Acknowledgements

Thank you to the Digital Engagement Lab at the University of Maryland for their support with this project. Check them out here: https://www.digitalengagementlab.org/