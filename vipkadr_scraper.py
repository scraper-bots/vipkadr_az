import asyncio
import aiohttp
import json
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class VipKadrScraper:
    def __init__(self, max_concurrent=10, delay=1):
        self.base_url = "https://vipkadr.az"
        self.max_concurrent = max_concurrent
        self.delay = delay
        self.session = None
        self.scraped_data = []
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str, retries=3) -> Optional[str]:
        """Fetch a single page with retry logic"""
        for attempt in range(retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        pass
                        return content
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except Exception as e:
                logger.error(f"Error fetching {url} (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
        return None
    
    def extract_job_urls_from_listing(self, html_content: str) -> List[str]:
        """Extract job URLs from a listing page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        job_urls = []
        
        # Find all job listing items
        job_items = soup.find_all('div', class_='ty-column5')
        
        for item in job_items:
            onclick_attr = item.get('onclick', '')
            if 'window.open(' in onclick_attr:
                # Extract URL from onclick="window.open('URL')"
                url_match = re.search(r"window\.open\('([^']+)'\)", onclick_attr)
                if url_match:
                    relative_url = url_match.group(1)
                    full_url = urljoin(self.base_url, relative_url)
                    job_urls.append(full_url)
        
        return job_urls
    
    def extract_job_details(self, html_content: str, job_url: str) -> Dict:
        """Extract detailed job information from individual job page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        job_data = {
            'url': job_url,
            'title': '',
            'salary': '',
            'company': '',
            'contact_person': '',
            'phone': '',
            'email': '',
            'city': '',
            'work_type': '',
            'experience': '',
            'education': '',
            'gender': '',
            'age': '',
            'description': '',
            'requirements': '',
            'added_date': '',
            'end_date': '',
            'job_id': '',
            'views': ''
        }
        
        try:
            # Extract title
            title_elem = soup.find('h3', class_='fpname')
            if title_elem:
                job_data['title'] = title_elem.get_text(strip=True)
            
            # Extract job ID and views
            view_count_elem = soup.find('div', class_='view_count')
            if view_count_elem:
                view_text = view_count_elem.get_text()
                job_id_match = re.search(r'#(\d+)', view_text)
                if job_id_match:
                    job_data['job_id'] = job_id_match.group(1)
                
                views_match = re.search(r'Baxış.*?(\d+)', view_text)
                if views_match:
                    job_data['views'] = views_match.group(1)
            
            # Extract company
            company_elem = soup.find('div', class_='view_count', style='margin-top: 10px')
            if company_elem:
                company_text = company_elem.get_text()
                if 'Şirkət' in company_text:
                    job_data['company'] = company_text.replace('Şirkət :', '').strip()
            
            # Extract product features (salary, contact info, etc.)
            feature_divs = soup.find_all('div', class_='ty-product-feature')
            for feature in feature_divs:
                label_elem = feature.find('span', class_='ty-product-feature__label')
                value_elem = feature.find('div', class_='ty-product-feature__value')
                
                if label_elem and value_elem:
                    label = label_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    
                    if 'Maaş' in label:
                        job_data['salary'] = value
                    elif 'Əlaqədar şəxs' in label:
                        job_data['contact_person'] = value
                    elif 'Telefon' in label:
                        # Extract phone from link
                        phone_link = value_elem.find('a')
                        if phone_link:
                            job_data['phone'] = phone_link.get_text(strip=True)
                        else:
                            job_data['phone'] = value
                    elif 'Email' in label:
                        # Extract email from link
                        email_link = value_elem.find('a')
                        if email_link:
                            href = email_link.get('href', '')
                            if href.startswith('mailto:'):
                                job_data['email'] = href.replace('mailto:', '').split('?')[0]
                        else:
                            job_data['email'] = value
                    elif 'Əlavə olunma tarixi' in label:
                        job_data['added_date'] = value
                    elif 'Bitmə tarixi' in label:
                        job_data['end_date'] = value
                    elif 'İş vaxtı' in label:
                        job_data['work_type'] = value
                    elif 'Şəhər' in label:
                        job_data['city'] = value
                    elif 'İş təcrübəsi' in label:
                        job_data['experience'] = value
                    elif 'Cins' in label:
                        job_data['gender'] = value
                    elif 'Yaş' in label:
                        job_data['age'] = value
            
            # Extract description
            desc_elem = soup.find('div', class_='descriptions')
            if desc_elem:
                # Get first div content (job description)
                first_div = desc_elem.find('div')
                if first_div:
                    job_data['description'] = first_div.get_text(strip=True).replace('<br>', '\n')
            
            # Extract requirements (from "Tələblər" section)
            req_section = None
            h3_elements = soup.find_all('h3')
            for h3 in h3_elements:
                if 'Tələblər' in h3.get_text():
                    req_section = h3.find_next_sibling('div')
                    break
            
            if req_section:
                job_data['requirements'] = req_section.get_text(strip=True).replace('<br>', '\n')
        
        except Exception as e:
            logger.error(f"Error parsing job details for {job_url}: {e}")
        
        return job_data
    
    async def scrape_listing_page(self, page_num: int) -> List[str]:
        """Scrape a single listing page and return job URLs"""
        url = f"{self.base_url}/cv-bazasi/?page={page_num}"
        
        html_content = await self.fetch_page(url)
        if not html_content:
            return []
        
        job_urls = self.extract_job_urls_from_listing(html_content)
        pass
        
        return job_urls
    
    async def scrape_job_detail(self, job_url: str) -> Optional[Dict]:
        """Scrape detailed information from a single job page"""
        html_content = await self.fetch_page(job_url)
        if not html_content:
            return None
        
        job_data = self.extract_job_details(html_content, job_url)
        await asyncio.sleep(self.delay)  # Rate limiting
        
        return job_data
    
    async def scrape_all_pages(self, start_page=1, end_page=None):
        """Scrape all listing pages to get job URLs"""
        if end_page is None:
            # First, find the last page number
            first_page_content = await self.fetch_page(f"{self.base_url}/cv-bazasi/?page=1")
            if first_page_content:
                soup = BeautifulSoup(first_page_content, 'html.parser')
                # Try to find pagination to determine last page
                # This might need adjustment based on the actual pagination structure
                end_page = 50  # Default fallback
        
        pass
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def scrape_page_with_semaphore(page_num):
            async with semaphore:
                return await self.scrape_listing_page(page_num)
        
        # Scrape all listing pages concurrently
        tasks = [scrape_page_with_semaphore(page) for page in range(start_page, end_page + 1)]
        all_job_urls_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten the list and filter out exceptions
        all_job_urls = []
        for urls_list in all_job_urls_lists:
            if isinstance(urls_list, list):
                all_job_urls.extend(urls_list)
            else:
                logger.error(f"Error in page scraping: {urls_list}")
        
        # Remove duplicates
        unique_job_urls = list(set(all_job_urls))
        pass
        
        return unique_job_urls
    
    async def scrape_all_jobs(self, job_urls: List[str]):
        """Scrape detailed information for all job URLs"""
        pass
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def scrape_job_with_semaphore(job_url):
            async with semaphore:
                return await self.scrape_job_detail(job_url)
        
        # Scrape all job details concurrently
        tasks = [scrape_job_with_semaphore(url) for url in job_urls]
        job_details = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None values and exceptions
        valid_jobs = []
        for job_data in job_details:
            if isinstance(job_data, dict) and job_data:
                valid_jobs.append(job_data)
            elif not isinstance(job_data, dict):
                logger.error(f"Error scraping job: {job_data}")
        
        self.scraped_data = valid_jobs
        pass
        
        return valid_jobs
    
    def save_to_csv(self, filename: str = "vipkadr_jobs.csv"):
        """Save scraped data to CSV file"""
        if not self.scraped_data:
            logger.warning("No data to save")
            return
        
        fieldnames = [
            'job_id', 'title', 'company', 'salary', 'city', 'work_type',
            'experience', 'education', 'gender', 'age', 'contact_person',
            'phone', 'email', 'description', 'requirements', 'added_date',
            'end_date', 'views', 'url'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.scraped_data)
        
        pass
    
    def save_to_json(self, filename: str = "vipkadr_jobs.json"):
        """Save scraped data to JSON file"""
        if not self.scraped_data:
            logger.warning("No data to save")
            return
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.scraped_data, jsonfile, ensure_ascii=False, indent=2)
        
        pass


async def main():
    """Main function to run the scraper"""
    start_time = time.time()
    
    async with VipKadrScraper(max_concurrent=15, delay=0.5) as scraper:
        try:
            # Step 1: Get all job URLs from listing pages
            job_urls = await scraper.scrape_all_pages(start_page=1, end_page=20)  # Adjust range as needed
            
            if not job_urls:
                logger.error("No job URLs found")
                return
            
            # Step 2: Scrape detailed information for all jobs
            await scraper.scrape_all_jobs(job_urls)
            
            # Step 3: Save data
            scraper.save_to_csv("vipkadr_jobs.csv")
            scraper.save_to_json("vipkadr_jobs.json")
            
            end_time = time.time()
            logger.info(f"Scraping completed in {end_time - start_time:.2f} seconds")
            logger.info(f"Total jobs scraped: {len(scraper.scraped_data)}")
            
        except Exception as e:
            logger.error(f"Error in main execution: {e}")


if __name__ == "__main__":
    asyncio.run(main())