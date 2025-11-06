import time
from random import uniform
import json
import time
import random
import pandas as pd
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


def main() -> None:
    driver = get_driver()
    try:
        login(driver)
        print("Logged in OK")

        urls = read_urls("urls.txt")
        print(f"Found {len(urls)} URLs, processing all...")

        rows = []

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            
            driver.get(url)
            
            wait_for_profile_loaded(driver)
            
            # Expand "See more" buttons to get full content
            expand_see_more(driver)
            
            # Scroll to bottom with human-like behavior
            human_scroll(driver, total_pause_sec=6)
            
            # Optional: save HTML for debugging (comment out if not needed)
            # save_html(driver, url)
            
            # Get page source and parse
            html = driver.page_source
            record = parse_profile(html)
            
            # Fill live-only fields
            record["profile_url"] = url
            record["last_scraped_at"] = now_utc_iso()
            record["experiences_json"] = json.dumps(record["experiences_json"], ensure_ascii=False)
            record["education_json"] = json.dumps(record["education_json"], ensure_ascii=False)
            
            rows.append(record)
            print(f"  Extracted: {record.get('full_name', 'N/A')}")
            
            # Polite delay before next profile (except for last)
            if i < len(urls):
                sleep_time = random.uniform(8, 15)
                print(f"  Waiting {sleep_time:.1f}s before next profile...")
                time.sleep(sleep_time)

        print(f"\nProcessed {len(rows)} profiles. Writing CSV...")
        
        # Write CSV
        df = pd.DataFrame(rows, columns=[
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
        ])
        df.to_csv("profiles.csv", index=False)
        print(f"Saved to profiles.csv")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    main()