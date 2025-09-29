from scraper.scrape_data import *
from downloader.download_data import *
from audio_preprocessor.remove_trailing_audio import *
from audio_preprocessor.rename_files import *
from text_preprocessor.preprocess_transcript import *
from text_preprocessor.rename_files import *
from train_manifest.create_manifest import *
from dashboard.process_data import *
import subprocess
import argparse


def get_args():
    parser = argparse.ArgumentParser(description="NPTEL YouTube Audio Scraper/Downloader.")
    parser.add_argument("course_url", type=str, help="The NPTEL course URL to scrape.")
    parser.add_argument("--download", action="store_true", help="Download audio from saved JSON file.")
    parser.add_argument("--json", type=str, default="data/video_links.json", help="Path to JSON file.")
    return parser.parse_args()

args = get_args()
COURSE_URL = args.course_url

def main():
    # Define the folder name
    folder_name = 'data'
    # Check if it exists, if not, create it
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"✅ Folder '{folder_name}' created.")
    else:
        print(f"ℹ️ Folder '{folder_name}' already exists.")

    args = get_args()
    driver = setup_driver()
    ## Scrape audio and transcript data from NPTEL site
    get_week_elements(driver, args.json)
    get_transcript_links(args.course_url)
    print("✅ All video links and transcript links saved to:", args.json)

    ## Download audio files and transcripts from the scraped JSON file
    download_audio_from_json(args.json)
    download_transcripts("data/transcripts.json", "data/transcript_downloads")
    print("✅ All audio files and transcripts downloaded.")

    ## Preprocess audio files
    bash_script_path = "audio_preprocessor/preprocess_audio.sh"
    subprocess.run(['wsl', 'bash', bash_script_path,'data/audio_downloads','data/audio_wav','4' ])

    ## Remove trailing audio from the downloaded files
    trim_trailing_audio("data/audio_wav", "data/audio_processed", 10)
    print("✅ All audio files converted and trimmed and saved to:", "data/audio_processed")

    ## preprocess transcripts
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
    process_manifest("train_manifest.jsonl", "dashboard/processed_data.csv")
    print("✅ Processed data for Grafana.")
    
    ## Create SQLite database
    process_manifest("train_manifest.jsonl", "dashboard/dashboard_data.db")
    print("✅ SQLite database created.")

    driver.quit()
    print("✅ All tasks completed successfully.")

if __name__ == "__main__":
    main()

