# Misinformation App
A mobile app dedicated to reviewing news articles for misinformation using Claude AI.

## Tech Stack
**Framework and Runtime**
* Python 

**AI and Content Processing**
* **Anthropic SDK (v0.84.0)** - Claude API Integration <br>
* [NewsAPI](https://newsapi.org/)

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
Articles are scored based off 7 factors and their respective weighting: <br>
1.  
2. 
3. 
4. 
5. 
6. 
7. 


## Project Structure

```
backend/
├── fetch_articles.py          # Article fetch
├── main.py                    # Main testpoint
├── pipeline.py                # Main pipeline
├── scorer.py                  # AI scorer
├── scraper.py                 # Article scraper
frontend/
├── app/    
├── components/
├── constants/                 
├── hooks/
└── types/                     # TypeScript type definitions
│
```

## Getting Started
1. Install dependencies
```bash
npm install
pip install -r requirements.txt
```
2. Fill Environment Variables <br>
There are two .env.local files needed.
Create a ```bash .env.local``` file in the backend folder with the following variables:
```bash
NEWS_API_KEY = your_news_api_key
ANTHROPIC_API_KEY = your_anthropic_api_key
```
Create a ```bash .env.local``` file in the frontend folder with the following variables:
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
4. Start App <br>
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

## Acknowledgements
I'll fill this out later
