# Twitter Complaints Scraper and Analyzer

An intelligent system for scraping user complaints and issues from X (Twitter), supporting bilingual (Chinese/English) analysis with automatic classification by date and difficulty level.

## 🌟 Features

- **Dual-mode Data Scraping**: Supports both Twitter API and Selenium web scraping
- **Bilingual Analysis**: Automatic language detection with appropriate sentiment analysis for Chinese and English
- **Multi-dimensional Classification**:
  - Date-based organization
  - Difficulty levels (Easy/Medium/Hard)
  - Problem categories (Technical/Usability/Feature Request, etc.)
- **Sentiment Analysis**: Identifies positive, negative, and neutral emotions
- **Automatic Report Generation**: Generates reports in JSON and Excel formats
- **Keyword Extraction**: Automatically extracts trending complaint keywords

## 📋 System Requirements

- Python 3.8+
- Chrome browser (for Selenium mode)
- Twitter API credentials (for API mode)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd twitter-complaints-analyzer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit the `.env` file with your Twitter API credentials (if using API mode):

```
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

### 4. Run the System

Basic usage:
```bash
python main.py
```

Specify search keywords:
```bash
python main.py -k "ChatGPT" "OpenAI" "Claude"
```

More options:
```bash
python main.py -k "ProductName" -n 200 -d 14
```

Parameters:
- `-k, --keywords`: Search keywords (can specify multiple)
- `-n, --max-tweets`: Maximum tweets per keyword (default: 100)
- `-d, --days`: Search tweets from past N days (default: 7)
- `--no-api`: Use web scraping instead of API

## 📂 Project Structure

```
twitter-complaints-analyzer/
├── src/
│   ├── twitter_scraper.py    # Twitter data scraping module
│   ├── text_analyzer.py      # Text analysis module
│   └── data_manager.py       # Data management module
├── data/                     # Data storage directory
│   ├── raw/                  # Raw tweet data
│   ├── processed/            # Processed data
│   ├── by_date/             # Data organized by date
│   ├── by_difficulty/       # Data organized by difficulty
│   ├── by_category/         # Data organized by category
│   └── reports/             # Analysis reports
├── config.py                # Configuration file
├── main.py                  # Main program
├── requirements.txt         # Dependencies
└── .env.example            # Environment variables example
```

## 🔍 Analysis Dimensions

### 1. Sentiment Analysis
- **Positive**: Satisfied, appreciative feedback
- **Negative**: Complaints and issues
- **Neutral**: Objective statements or suggestions

### 2. Difficulty Levels
- **🟢 Easy**: Minor issues, quick fixes
- **🟡 Medium**: General issues requiring moderate effort
- **🔴 Hard**: Critical issues requiring significant work

### 3. Problem Categories
- **Technical**: Bugs, crashes, performance issues
- **Usability**: UI/UX related problems
- **Feature Request**: New feature demands
- **Performance**: Speed, resource usage
- **Compatibility**: Version, platform compatibility
- **Service**: Customer service, support related

## 📊 Output Formats

### JSON Report Example
```json
{
  "timestamp": "20240115_143022",
  "total_tweets": 150,
  "date_range": {
    "start": "2024-01-08",
    "end": "2024-01-15"
  },
  "sentiment_distribution": {
    "negative": 89,
    "neutral": 45,
    "positive": 16
  },
  "difficulty_distribution": {
    "easy": 30,
    "medium": 65,
    "hard": 55
  }
}
```

### Excel Report
The system generates Excel files with the following sheets:
- **All Tweets**: Detailed information for all tweets
- **Easy/Medium/Hard Issues**: Tweets classified by difficulty
- **Summary**: Summary statistics

## 🛠 Advanced Usage

### Using the Python API

```python
from src.twitter_scraper import TwitterScraper
from src.text_analyzer import TextAnalyzer
from src.data_manager import DataManager

# Initialize components
scraper = TwitterScraper(use_api=True)
analyzer = TextAnalyzer()
manager = DataManager()

# Scrape tweets
tweets = scraper.search_complaints(["ProductName"], max_results=100)

# Analyze tweets
analyzed = [analyzer.analyze_tweet(tweet) for tweet in tweets]

# Save results
manager.save_analyzed_data(analyzed)
```

### Customizing Analysis Rules

Edit the keyword dictionaries in `src/text_analyzer.py` to customize:
- Problem category keywords
- Difficulty assessment indicators
- Sentiment analysis vocabulary

## ⚠️ Important Notes

1. **API Limits**: Twitter API has rate limits, use responsibly
2. **Privacy**: Comply with relevant laws and protect user privacy
3. **Accuracy**: Automated analysis may have errors, manual review recommended for important conclusions
4. **Proxy Settings**: Configure proxy in `.env` file if needed

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

## 📧 Contact

For questions or suggestions, please submit an Issue.