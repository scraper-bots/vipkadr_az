# VipKadr.az Job Scraper

A high-performance async web scraper for extracting job listings from VipKadr.az using Python, asyncio, and aiohttp.

## Features

- **Fast Async Scraping**: Uses asyncio and aiohttp for concurrent HTTP requests
- **Complete Job Data**: Extracts all available job details including:
  - Job title, company, salary
  - Contact information (phone, email, contact person)
  - Job requirements and description
  - Location, work type, experience level
  - Posted and expiry dates
- **Rate Limiting**: Built-in delays and concurrent request limiting to be respectful
- **Error Handling**: Robust error handling with retry logic
- **Multiple Output Formats**: Saves data in both CSV and JSON formats
- **Progress Tracking**: Real-time logging and progress information

## Installation

1. Clone or download the files
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Test (recommended first)
```bash
python test_scraper.py
```
This will scrape 2 pages and 5 job details as a test.

### Full Scraping
```bash
python run_full_scrape.py
```

### Custom Options
```bash
# Scrape specific page range
python run_full_scrape.py --start-page 1 --end-page 20

# Adjust concurrency (default: 10)
python run_full_scrape.py --concurrent 15

# Get help
python run_full_scrape.py --help
```

## Files

- `vipkadr_scraper.py` - Main scraper class
- `test_scraper.py` - Test script for small batch
- `run_full_scrape.py` - Production script for full scraping
- `requirements.txt` - Python dependencies

## Output Files

The scraper generates several output files:

- `vipkadr_jobs_YYYYMMDD_HHMMSS.csv/json` - Timestamped results
- `vipkadr_jobs_latest.csv/json` - Latest results (overwritten each run)
- `test_results.csv/json` - Test run results

## Data Structure

Each job record contains:

```json
{
  "job_id": "44269",
  "title": "İDARƏETMƏ İŞİ TƏKLİF EDİLİR",
  "company": "BTK Group",
  "salary": "1200 AZN",
  "contact_person": "Təranə x",
  "phone": "0503583399",
  "email": "taranaxalilova1960@gmail.com",
  "city": "Bakı",
  "work_type": "Tam İş saatı",
  "experience": "1 ildən aşağı",
  "gender": "Fərq etmir",
  "age": "25 - 65",
  "description": "Job description...",
  "requirements": "Job requirements...",
  "added_date": "24 İyn 2025",
  "end_date": "24 İyl 2025",
  "views": "167",
  "url": "https://vipkadr.az/..."
}
```

## Performance

- **Test Results**: Successfully scraped 5 jobs from 2 pages in ~10 seconds
- **Concurrent Processing**: Up to 15 concurrent requests (adjustable)
- **Rate Limiting**: 0.3-1 second delays between requests
- **Efficiency**: ~2-3 seconds per job on average

## Respectful Scraping

The scraper is designed to be respectful:
- Rate limiting with configurable delays
- Concurrent request limits
- Proper error handling and retries
- User-Agent headers

## Error Handling

- Automatic retries for failed requests
- Graceful handling of network errors
- Saves partial results if interrupted
- Detailed logging for debugging

## Example Usage

```python
import asyncio
from vipkadr_scraper import VipKadrScraper

async def custom_scrape():
    async with VipKadrScraper(max_concurrent=5, delay=1) as scraper:
        job_urls = await scraper.scrape_all_pages(start_page=1, end_page=5)
        await scraper.scrape_all_jobs(job_urls)
        scraper.save_to_csv("my_results.csv")

asyncio.run(custom_scrape())
```

## Legal Notice

This scraper is for educational and research purposes. Please respect the website's terms of service and robots.txt file. Use responsibly and ethically.