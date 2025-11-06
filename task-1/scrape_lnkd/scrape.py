import time
from random import uniform

from utils import (
    get_driver,
    login,
    read_urls,
    wait_for_profile_loaded,
    human_scroll,
    save_html,
)


def main() -> None:
    driver = get_driver()
    try:
        login(driver)
        print("Logged in OK")

        urls = read_urls("urls.txt")
        print(f"Found {len(urls)} URLs, processing first 3 (dry run)...")

        for i, url in enumerate(urls[:3], 1):
            print(f"\n[{i}/3] Processing: {url}")
            driver.get(url)

            wait_for_profile_loaded(driver)

            # Scroll to bottom with human-like behavior
            human_scroll(driver, total_pause_sec=5)

            # Optional pause at bottom (1-2s)
            time.sleep(uniform(1.0, 2.0))

            path = save_html(driver, url)
            print(f"Saved: {path}")

            # Sleep 8-15s before next profile (except for last)
            if i < 3:
                sleep_time = uniform(8.0, 15.0)
                print(f"Waiting {sleep_time:.1f}s before next profile...")
                time.sleep(sleep_time)

        print("\nDry run complete!")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()