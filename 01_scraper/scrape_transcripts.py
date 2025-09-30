import os
import json
import argparse
import asyncio
from playwright.async_api import async_playwright


async def scrape_transcripts(course_url, output_json="data/transcripts.json"):
    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("📘 Opening course page...")
        await page.goto(course_url, timeout=60000)

        # Click Downloads tab
        print("🧭 Looking for 'Downloads' tab...")
        tabs = await page.query_selector_all(".tab")
        clicked = False
        for tab in tabs:
            text = (await tab.inner_text()).strip().lower()
            if text == "downloads":
                await tab.click()
                print("✅ Clicked on Downloads tab.")
                clicked = True
                break

        if not clicked:
            print("❌ 'Downloads' tab not found.")
            await browser.close()
            return

        # Open Transcripts section
        try:
            await page.wait_for_selector("h3:text('Transcripts')", timeout=10000)
            transcripts_header = await page.query_selector("h3:text('Transcripts')")
            await transcripts_header.click()
            print("📂 Opened Transcripts section.")
        except Exception as e:
            print(f"❌ Transcripts section not found: {e}")
            await browser.close()
            return

        # Grab all transcript divs
        await page.wait_for_selector("div.d-data")
        data_divs = await page.query_selector_all("div.d-data")
        print(f"📥 Found {len(data_divs)} transcript entries.\n")

        results = []

        for idx, div in enumerate(data_divs, start=1):
            print(f"➡️ Processing transcript {idx}")
            entry = {}

            # Title
            title_span = await div.query_selector("span.c-name")
            if title_span:
                entry["title"] = (await title_span.inner_text()).strip()
            else:
                print(f"⚠️ Skipping transcript {idx} (no title found)")
                continue

            # Open language dropdown
            try:
                dropdown = await div.query_selector(".pseudo-input")
                if dropdown:
                    await dropdown.click()
                    await asyncio.sleep(0.5)

                    options = await div.query_selector_all("ul.pseudo-options li")
                    clicked = False
                    for opt in options:
                        text = (await opt.inner_text()).strip().lower()
                        if "english-verified" in text:
                            await opt.click()
                            print("✅ Selected 'english-Verified'")
                            clicked = True
                            break
                    if not clicked:
                        print("⚠️ 'english-Verified' option not found.")
                        continue
            except:
                print("⚠️ No dropdown found, skipping.")
                continue

            # Transcript link
            try:
                link = await div.query_selector("a[href*='drive.google.com']")
                if link:
                    href = await link.get_attribute("href")
                    entry["link"] = href
                    print(f"🔗 Transcript link: {href}\n")
                else:
                    print("⚠️ Google Drive link not found.\n")
                    continue
            except Exception as e:
                print(f"⚠️ Error fetching link: {e}")
                continue

            # Only save if link exists
            if "link" in entry:
                results.append(entry)

        await browser.close()

        # Save results
        if results:
            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved {len(results)} transcript links to {output_json}")
        else:
            print("❌ No transcript links found to save.")


def get_args():
    parser = argparse.ArgumentParser(description="NPTEL Transcript Scraper (Playwright).")
    parser.add_argument("course_url", type=str, help="The NPTEL course URL to scrape.")
    parser.add_argument("--json", type=str, default="data/transcripts.json", help="Path to save the JSON file.")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    asyncio.run(scrape_transcripts(args.course_url, args.json))
