import asyncio
import json
import argparse
from playwright.async_api import async_playwright

async def scrape_nptel_course(course_url, json_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(course_url)
        print(f"📘 Loaded course page: {course_url}")
        await page.wait_for_timeout(3000)

        # Find all week sections
        week_spans = await page.locator(
            "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'week')]"
        ).all()
        print(f"🔎 Found {len(week_spans)} week sections.")

        data = []

        for i, week in enumerate(week_spans):
            # Re-locate week spans each time (DOM may change)
            week_spans = await page.locator(
                "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'week')]"
            ).all()
            week = week_spans[i]
            week_text = (await week.text_content()).strip()
            print(f"\n📂 Opening {week_text}...")
            await week.scroll_into_view_if_needed()
            await week.click()
            await page.wait_for_timeout(2000)

            # Find all lessons in this week
            try:
                lesson_items = await page.locator(".lessons-list li").all()
                print(f"  📑 Found {len(lesson_items)} lessons.")
                for j in range(len(lesson_items)):
                    # Re-locate lesson items each time to avoid stale references
                    lesson_items = await page.locator(".lessons-list li").all()
                    if j >= len(lesson_items):
                        continue
                    li = lesson_items[j]
                    lesson_title = (await li.text_content()).strip()
                    if not lesson_title:
                        continue
                    print(f"    🎥 Lesson: {lesson_title}")
                    try:
                        await li.scroll_into_view_if_needed()
                        await li.click(force=True)  # Use force=True to bypass overlays
                        await page.wait_for_timeout(2000)
                        # Wait for YouTube iframe
                        try:
                            await page.wait_for_selector("iframe[src*='youtube.com']", timeout=5000)
                            frames = page.frames
                            youtube_link = None
                            for frame in frames:
                                # Try to find a YouTube link in each frame
                                links = await frame.query_selector_all("a[href*='youtube.com/watch']")
                                for link in links:
                                    href = await link.get_attribute("href")
                                    if href and "youtube.com/watch" in href:
                                        youtube_link = href
                                        break
                                if youtube_link:
                                    break
                            if youtube_link:
                                print(f"      ✅ YouTube Link: {youtube_link}")
                                data.append({"lesson_title": lesson_title, "youtube_link": youtube_link})
                            else:
                                print(f"      ⚠️ Skipped: No YouTube link found in lesson '{lesson_title}'")
                        except Exception as e:
                            if "Timeout" in str(e):
                                print(f"      ⚠️ Skipped: No YouTube iframe found for lesson '{lesson_title}'")
                            else:
                                print(f"      ⚠️ Skipped: {e}")
                    except Exception as e:
                        print(f"      ⚠️ Skipped: {e}")
                        await page.keyboard.press("Escape")  # Try to close overlays if any
                        await page.wait_for_timeout(500)
            except Exception as e:
                print(f"  ❌ No lessons found in {week_text}: {e}")

        # Save results
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved {len(data)} entries to {json_path}")
        await browser.close()

def main():
    parser = argparse.ArgumentParser(description="Scrape NPTEL course YouTube links using Playwright.")
    parser.add_argument("course_url", help="URL of the NPTEL course")
    parser.add_argument("--json", default="data/output.json", help="Path to output JSON file")
    args = parser.parse_args()
    asyncio.run(scrape_nptel_course(args.course_url, args.json))

if __name__ == "__main__":
    main()