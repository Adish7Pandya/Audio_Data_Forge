import os
import time
import json
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")  
    return webdriver.Chrome(options=options)

def scrape_transcripts(course_url, output_json="data/transcripts.json"):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    driver.get(course_url)
    print("📘 Opening course page...")
    time.sleep(3)

    # Click on the Downloads tab
    print("🧭 Looking for 'Downloads' tab...")
    tabs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tab")))
    for tab in tabs:
        if tab.text.strip().lower() == "downloads":
            tab.click()
            print("✅ Clicked on Downloads tab.")
            break
    else:
        print("❌ 'Downloads' tab not found.")
        driver.quit()
        return

    time.sleep(2)

    # Click on the Transcripts section
    try:
        transcripts_header = wait.until(
            EC.presence_of_element_located((By.XPATH, "//h3[text()='Transcripts']"))
        )
        transcripts_header.click()
        print("📂 Opened Transcripts section.")
    except Exception as e:
        print(f"❌ Transcripts section not found: {e}")
        driver.quit()
        return

    time.sleep(2)

    # Process all transcript entries
    data_divs = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.d-data"))
    )
    print(f"📥 Found {len(data_divs)} transcript entries.\n")

    results = []

    for idx, div in enumerate(data_divs, start=1):
        print(f"➡️ Processing transcript {idx}")
        entry = {}

        try:
            # Get title if available
            try:
                title_span = div.find_element(By.CSS_SELECTOR, "span.c-name")
                entry["title"] = title_span.text.strip()
            except:
                entry["title"] = f"Transcript {idx}"

            time.sleep(1)

            # Click language dropdown
            dropdown = div.find_element(By.CSS_SELECTOR, ".pseudo-input")
            dropdown.click()
            time.sleep(1)

            # Click "english-Verified"
            options = div.find_elements(By.CSS_SELECTOR, "ul.pseudo-options li")
            clicked = False
            for opt in options:
                if "english-verified" in opt.text.strip().lower():
                    opt.click()
                    print("✅ Selected 'english-Verified'")
                    clicked = True
                    time.sleep(1)
                    break

            if not clicked:
                print("⚠️ 'english-Verified' option not found.")
                continue

            # Get Google Drive link
            try:
                link = div.find_element(By.CSS_SELECTOR, "a[href*='drive.google.com']")
                href = link.get_attribute("href")
                print(f"🔗 Transcript link: {href}\n")
                entry["link"] = href
                results.append(entry)
            except Exception:
                print("⚠️ Google Drive link not found.\n")

        except Exception as e:
            print(f"⚠️ Error processing transcript {idx}: {e}\n")

    driver.quit()

    # Save results
    if results:
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved {len(results)} transcript links to {output_json}")
    else:
        print("❌ No transcript links found to save.")

def get_args():
    parser = argparse.ArgumentParser(description="NPTEL Transcript Scraper.")
    parser.add_argument("course_url", type=str, help="The NPTEL course URL to scrape.")
    parser.add_argument("--json", type=str, default="data/transcripts.json", help="Path to save the JSON file.")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    scrape_transcripts(args.course_url, args.json)
