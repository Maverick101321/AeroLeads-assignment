import time
from random import uniform
import json
import traceback
import random
import pandas as pd
import os
import logging
import argparse
from parser import parse_profile
from utils import (
    get_driver,
    login,
    read_urls,
    wait_for_profile_loaded,
    human_scroll,
    save_html,
    expand_see_more,
    now_utc_iso
)


def setup_logging():
    """Configure logging to both file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scrape.log', mode='a'),
            logging.StreamHandler()
        ]
    )


def load_seen_urls(csv_path: str = "profiles.csv") -> set:
    """
    Read existing profiles.csv and return a set of already-scraped URLs.
    """
    seen = set()
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            if "profile_url" in df.columns:
                seen = set(df["profile_url"].dropna().astype(str))
                logging.info(f"Found {len(seen)} already-scraped URLs in {csv_path}")
        except Exception as e:
            logging.warning(f"Could not read {csv_path}: {e}")
    return seen


def main(force: bool = False) -> None:
    setup_logging()
    logging.info("=" * 60)
    logging.info("Starting LinkedIn profile scraper")
    logging.info("=" * 60)
    
    driver = get_driver()
    try:
        logging.info("Logging in to LinkedIn...")
        login(driver)
        logging.info("Logged in OK")

        urls = read_urls("urls.txt")
        logging.info(f"Found {len(urls)} URLs in urls.txt")
        
        # Load already-scraped URLs
        seen_urls = set() if force else load_seen_urls()
        
        # Filter URLs to process
        urls_to_process = [url for url in urls if url not in seen_urls]
        skipped_count = len(urls) - len(urls_to_process)
        
        if skipped_count > 0:
            logging.info(f"Skipping {skipped_count} already-scraped URLs (use --force to re-scrape)")
        
        if not urls_to_process:
            logging.info("All URLs already scraped. Exiting.")
            return
        
        logging.info(f"Processing {len(urls_to_process)} URLs...")

        rows = []
        errors = []
        consecutive_failures = 0
        base_sleep_min = 8
        base_sleep_max = 15
        
        # CSV columns
        profile_columns = [
            "profile_url",
            "full_name",
            "headline",
            "location",
            "about",
            "current_position_title",
            "current_position_company",
            "current_position_dates",
            "experiences_json",
            "education_json",
            "skills",
            "last_scraped_at",
        ]
        
        error_columns = [
            "profile_url",
            "error_type",
            "error_message",
            "when",
            "ts",
        ]
        
        # Track file existence for header writing
        profiles_file_exists = os.path.exists("profiles.csv")
        errors_file_exists = os.path.exists("errors.csv")

        for i, url in enumerate(urls_to_process, 1):
            logging.info(f"[{i}/{len(urls_to_process)}] Starting: {url}")
            print(f"\n[{i}/{len(urls_to_process)}] Processing: {url}")
            
            try:
                when = "load"
                driver.get(url)
                
                when = "wait_for_profile"
                wait_for_profile_loaded(driver)
                
                when = "expand_see_more"
                # Expand "See more" buttons to get full content
                expand_see_more(driver)
                logging.info(f"  See more buttons expanded for {url}")
                
                when = "scroll"
                # Scroll to bottom with human-like behavior
                human_scroll(driver, total_pause_sec=6)
                
                when = "parse"
                # Optional: save HTML for debugging (comment out if not needed)
                # save_html(driver, url)
                
                # Get page source and parse
                html = driver.page_source
                record = parse_profile(html)
                
                when = "write_csv"
                # Fill live-only fields
                record["profile_url"] = url
                record["last_scraped_at"] = now_utc_iso()
                record["experiences_json"] = json.dumps(record["experiences_json"], ensure_ascii=False)
                record["education_json"] = json.dumps(record["education_json"], ensure_ascii=False)
                
                rows.append(record)
                name = record.get('full_name', 'N/A')
                logging.info(f"  Extracted: {name}")
                print(f"  Extracted: {name}")
                
                # Persist row-by-row: append immediately
                df = pd.DataFrame([record], columns=profile_columns)
                df.to_csv("profiles.csv", mode='a', header=not profiles_file_exists, index=False)
                profiles_file_exists = True  # After first write, header is written
                logging.info(f"  Row written to profiles.csv for {url}")
                
                # Reset consecutive failures on success
                consecutive_failures = 0
                
            except Exception as e:
                # Capture error details
                error_type = type(e).__name__
                error_message = str(e)[:300]  # Trim to ~300 chars
                ts = now_utc_iso()
                
                # Get truncated traceback
                tb_lines = traceback.format_exc().split('\n')
                truncated_tb = '\n'.join(tb_lines[-10:])  # Last 10 lines of traceback
                
                errors.append({
                    "profile_url": url,
                    "error_type": error_type,
                    "error_message": error_message,
                    "when": when,
                    "ts": ts,
                })
                
                logging.error(f"  ERROR at {when} for {url}: {error_type}: {error_message}")
                logging.error(f"  Traceback (truncated):\n{truncated_tb}")
                print(f"  ERROR at {when}: {error_type}: {error_message}")
                
                # Write error to CSV immediately
                error_df = pd.DataFrame([errors[-1]], columns=error_columns)
                error_df.to_csv("errors.csv", mode='a', header=not errors_file_exists, index=False)
                errors_file_exists = True  # After first write, header is written
                
                # Increment consecutive failures for backoff
                consecutive_failures += 1
            
            # Polite delay before next profile (except for last)
            if i < len(urls_to_process):
                # Add backoff: +10s per consecutive failure
                backoff_seconds = consecutive_failures * 10
                sleep_time = random.uniform(base_sleep_min, base_sleep_max) + backoff_seconds
                
                if consecutive_failures > 0:
                    logging.info(f"  Backoff: {consecutive_failures} consecutive failures, adding {backoff_seconds}s")
                
                logging.info(f"  Waiting {sleep_time:.1f}s before next profile...")
                print(f"  Waiting {sleep_time:.1f}s before next profile...")
                time.sleep(sleep_time)
            
            logging.info(f"[{i}/{len(urls_to_process)}] Finished: {url}")

        logging.info(f"Processed {len(rows)} profiles successfully, {len(errors)} errors.")
        print(f"\nProcessed {len(rows)} profiles successfully, {len(errors)} errors.")
        
    finally:
        driver.quit()
        logging.info("Driver closed. Scraping session ended.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape LinkedIn profiles")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-scrape URLs even if they already exist in profiles.csv"
    )
    args = parser.parse_args()
    
    main(force=args.force)