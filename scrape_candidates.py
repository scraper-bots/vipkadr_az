#!/usr/bin/env python3
"""
VipKadr.az Candidate Scraper - Scrapes all candidate data from job listings
"""

import asyncio
import time
from datetime import datetime
from vipkadr_scraper import VipKadrScraper

async def scrape_all_candidates():
    """Scrape all candidates from all pages by default"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("🚀 VipKadr.az Candidate Scraper")
    print("=" * 50)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Scraping ALL candidates from ALL pages...")
    
    start_time = time.time()
    
    # Auto-detect last page or use high default
    async with VipKadrScraper(max_concurrent=15, delay=0.2) as scraper:
        try:
            # Get all candidate URLs from all pages (1 to 100 to ensure we get everything)
            print("\n📋 Collecting candidate URLs from all pages...")
            job_urls = await scraper.scrape_all_pages(start_page=1, end_page=100)
            
            if not job_urls:
                print("❌ No candidate URLs found")
                return
                
            print(f"✅ Found {len(job_urls)} unique candidate listings")
            
            # Scrape all candidate details
            print(f"\n🔍 Extracting detailed information for {len(job_urls)} candidates...")
            await scraper.scrape_all_jobs(job_urls)
            
            if not scraper.scraped_data:
                print("❌ No candidate details were scraped")
                return
            
            # Save results
            csv_filename = f"vipkadr_candidates_{timestamp}.csv"
            json_filename = f"vipkadr_candidates_{timestamp}.json"
            
            print(f"\n💾 Saving candidate data...")
            scraper.save_to_csv(csv_filename)
            scraper.save_to_json(json_filename)
            
            # Also save as latest
            scraper.save_to_csv("vipkadr_candidates_latest.csv")
            scraper.save_to_json("vipkadr_candidates_latest.json")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Results summary
            print(f"\n🎉 SCRAPING COMPLETED!")
            print("=" * 50)
            print(f"⏱️  Total time: {duration:.2f} seconds ({duration/60:.1f} minutes)")
            print(f"📊 Candidates scraped: {len(scraper.scraped_data)}")
            print(f"⚡ Average time per candidate: {duration/len(scraper.scraped_data):.2f}s")
            
            # Contact info statistics
            with_phone = sum(1 for job in scraper.scraped_data if job.get('phone'))
            with_email = sum(1 for job in scraper.scraped_data if job.get('email'))
            
            print(f"\n📞 Contact Information:")
            print(f"   • Candidates with phone numbers: {with_phone} ({with_phone/len(scraper.scraped_data)*100:.1f}%)")
            print(f"   • Candidates with email addresses: {with_email} ({with_email/len(scraper.scraped_data)*100:.1f}%)")
            
            print(f"\n📁 Output Files:")
            print(f"   • {csv_filename}")
            print(f"   • {json_filename}")
            print(f"   • vipkadr_candidates_latest.csv")
            print(f"   • vipkadr_candidates_latest.json")
            
        except KeyboardInterrupt:
            print("\n⚠️  Scraping interrupted by user")
            if scraper.scraped_data:
                print(f"💾 Saving {len(scraper.scraped_data)} candidates scraped so far...")
                scraper.save_to_csv(f"vipkadr_candidates_interrupted_{timestamp}.csv")
                scraper.save_to_json(f"vipkadr_candidates_interrupted_{timestamp}.json")
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(scrape_all_candidates())