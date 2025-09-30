import os
import sys
import subprocess
import argparse
import asyncio

# Add the directories to Python path
sys.path.append('01_scraper')
sys.path.append('02_downloader')
sys.path.append('03_audio_preprocessor')
sys.path.append('04_text_preprocessor')
sys.path.append('05_train_manifest')
sys.path.append('06_dashboard')

from scrape_data import scrape_nptel_course
from scrape_transcripts import scrape_transcripts
from download_data import *
from clean_audio import *
from remove_trailing_audio import *
from rename_audio import *
from preprocess_transcript import *
from rename_transcripts import *
from create_manifest import *
from process_data import *


def get_args():
    parser = argparse.ArgumentParser(description="NPTEL YouTube Audio Scraper/Downloader.")
    parser.add_argument("course_url", type=str, help="The NPTEL course URL to scrape.")
    parser.add_argument("--download", action="store_true", help="Download audio from saved JSON file.")
    parser.add_argument("--json", type=str, default="data/video_links.json", help="Path to JSON file.")
    return parser.parse_args()

args = get_args()
COURSE_URL = args.course_url

async def main():
    # Define the folder name
    folder_name = 'data'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"✅ Folder '{folder_name}' created.")
    else:
        print(f"ℹ️ Folder '{folder_name}' already exists.")

    ## Scrape audio and transcript data from NPTEL site
    await scrape_nptel_course(args.course_url, args.json)
    await scrape_transcripts(args.course_url, "data/transcripts.json")
    print("✅ All video links and transcript links saved.")

    ## Download audio files and transcripts from the scraped JSON file
    download_audio_from_json(args.json)
    download_transcripts("data/transcripts.json", "data/transcript_downloads")
    print("✅ All audio files and transcripts downloaded.")

    ## Preprocess audio files
    bash_script_path = "03_audio_preprocessor/preprocess_audio.sh"
    subprocess.run(['bash', bash_script_path, 'data/audio_downloads', 'data/audio_wav', '4'])

    ## Remove trailing audio from the downloaded files
    trim_trailing_audio("data/audio_wav", "data/audio_processed", 10)
    print("✅ All audio files converted and trimmed and saved to:", "data/audio_processed")

    ## Preprocess transcripts
    process_all_transcripts("data/transcript_downloads", "data/transcript_processed")
    print("✅ All transcripts processed and saved to:", "data/transcript_processed")

    ## Rename audio files and transcripts to match
    rename_audio_files_in_dir("data/audio_processed")
    rename_transcript_files_in_dir("data/transcript_processed")
    print("✅ All files renamed.")

    ## Create manifest file
    create_training_manifest()
    print("✅ Manifest file created.")

    ## Process the data for Grafana
    process_manifest("train_manifest.jsonl", "06_dashboard/processed_data.csv")
    print("✅ Processed data for Grafana.")

    ## Create SQLite database
    process_manifest("train_manifest.jsonl", "06_dashboard/dashboard_data.db")
    print("✅ SQLite database created.")

    print("✅ All tasks completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())

    # 🚀 Launch dashboard after pipeline finishes
    app_path = os.path.join("06_dashboard", "app.py")
    subprocess.Popen([sys.executable, app_path])
    print("🌐 Dashboard started at http://127.0.0.1:8050")
