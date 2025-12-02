# Mobile Banking App Review Analysis System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)

## Overview

This repository contains an automated system for sentiment and thematic analysis of customer reviews from Ethiopian mobile banking applications. The system scrapes reviews from the Google Play Store, preprocesses the data, performs sentiment classification using VADER, identifies key themes (e.g., transaction performance, UI/UX), and stores results in a Dockerized PostgreSQL database for scalable querying.

### Key Features
- **Data Collection**: Scrapes up to 400 reviews per app using `google-play-scraper`.
- **Preprocessing**: Handles missing data, normalization, cleaning, and validation.
- **Analysis**: VADER-based sentiment scoring and keyword-driven thematic categorization.
- **Storage**: Loads processed data into PostgreSQL via Docker Compose for persistence.
- **Insights**: Generates reports on sentiment distribution, themes, keywords, and ratings (e.g., Dashen Bank: 73.3% positive; Bank of Abyssinia: 38.3%).
- **Reproducibility**: Jupyter notebooks and Python scripts for end-to-end execution.

Target Apps:
- Commercial Bank of Ethiopia (CBE)
- Bank of Abyssinia (BOA)
- Dashen Bank

**Total Reviews Analyzed**: 1,200 (400 per bank).

For detailed findings, see the [Interim Report (PDF)](interim.pdf).

## Project Structure
```
project/
├── data/
│   ├── raw/
│   │   ├── reviews.csv          # Scraped raw reviews
│   │   └── app_info.csv         # App metadata
│   └── processed/
│       ├── reviews_processed.csv    # Cleaned data
│       └── reviews_with_sentiment_themes.csv  # Analyzed data
├── notebooks/
│   └── runner.ipynb             # End-to-end Jupyter workflow
├── src/
│   ├── scrape.py                # Data scraping script
│   ├── pre.py                   # Preprocessing script
│   └── sentment.py              # Sentiment & thematic analysis
├── docker/
│   ├── Dockerfile               # Python loader image
│   └── docker-compose.yml       # Orchestrates DB + loader
├── load_to_postgres.py          # CSV to PostgreSQL loader
├── requirements.txt             # Python dependencies
├── interim.pdf                  # Full analysis report
└── README.md                    # This file
```

## Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/mobile-banking-review-analysis.git
   cd mobile-banking-review-analysis
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Prepare Data (Optional - Run Scraping)**
   If you don't have the `data/raw/` folder, run the scraper:
   ```bash
   python src/scrape.py
   ```
   This generates `data/raw/reviews.csv`.

4. **Run Preprocessing & Analysis**
   ```bash
   python src/pre.py          # Preprocess raw data
   python src/sentment.py     # Perform analysis
   ```
   Outputs: `data/processed/reviews_with_sentiment_themes.csv`.

5. **Dockerized Database Setup**
   Start PostgreSQL and load data:
   ```bash
   docker-compose up --build
   ```
   - This spins up the DB (`db` service) and runs the loader (`loader` service).
   - Data is mounted from `./notebooks/data` (ensure processed CSV is there).
   - Access DB: `docker-compose exec db psql -U postgres -d bank_reviews_db`.
   - Query example: `SELECT COUNT(*) FROM bank_reviews;` (should return 1200).

   Stop: `docker-compose down`.

## Usage

### End-to-End via Jupyter
```bash
# In notebooks/ directory
jupyter notebook runner.ipynb
```
This notebook orchestrates scraping, preprocessing, analysis, and visualization.

### Custom Queries on DB
Connect via `psql` or any SQL client:
```sql
-- Total reviews by bank
SELECT bank_name, COUNT(*) FROM bank_reviews GROUP BY bank_name;

-- Sentiment distribution
SELECT bank_name, 
       SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) AS positive,
       SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) AS negative
FROM bank_reviews 
GROUP BY bank_name;
```

### Generating Reports
The `interim.pdf` is pre-generated. To recreate visualizations:
```bash
python src/visualize.py  # Assumes matplotlib/seaborn in requirements
```

## Analysis Highlights
- **Sentiment**: Dashen Bank leads (73.3% positive), BOA lags (38.3%).
- **Top Theme**: Transaction Performance (30.8% of reviews).
- **Keywords**: "app", "transaction", "crash" dominate negatives.
- **Ratings**: Bimodal (39.8% 1-star, 32.9% 5-star).

See [interim.pdf](interim.pdf) for full details, recommendations, and future work.

## Contributing
1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.


---

*Stars, forks, and issues welcome! 🚀*
