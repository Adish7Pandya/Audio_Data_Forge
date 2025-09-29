import os
import json
import subprocess
from urllib.parse import parse_qs, urlparse
import argparse
import requests

def download_audio_from_json(json_path, output_folder="data/audio_downloads"):
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n📥 Starting download of {len(data)} items from {json_path}")
    for item in data:
        lesson_title = item["lesson_title"]
        youtube_link = item["youtube_link"]
        download_audio_from_youtube_links(youtube_link, lesson_title, output_folder)

def download_audio_from_youtube_links(youtube_link, lesson_title, output_folder="data/audio_downloads"):
    safe_title = "".join(c for c in lesson_title if c.isalnum() or c in " _-").rstrip()
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{safe_title}.%(ext)s")
    expected_files = [f for f in os.listdir(output_folder) if f.startswith(safe_title)]
    if expected_files:
        print(f"⚠️ Skipping {safe_title}, already exists.")
        return
    print(f"⬇️ Downloading audio for: {safe_title}")
    try:
        subprocess.run([
            "yt-dlp",
            "-f", "bestaudio",
            "-o", output_path,
            youtube_link
        ], check=True)
        print(f"🎧 Downloaded and saved as: {safe_title} (original audio format)\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ yt-dlp failed for {safe_title}: {e}")

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)
    if token:
        response = session.get(URL, params={"id": file_id, "confirm": token}, stream=True)
    if response.status_code == 200:
        with open(destination, "wb") as f:
            for chunk in response.iter_content(32768):
                if chunk:
                    f.write(chunk)
        return True
    else:
        return False

def download_transcripts(json_path="data/transcript_links.json", output_dir="data/transcript_downloads"):
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        return
    with open(json_path, "r", encoding="utf-8") as f:
        transcripts = json.load(f)
    print(f"📄 Downloading {len(transcripts)} transcripts...\n")
    for idx, entry in enumerate(transcripts, 1):
        title = entry.get("title", f"Transcript_{idx}")
        url = entry.get("link")
        try:
            print(url)
            parsed_url = urlparse(url)
            file_id = None
            if "id=" in url:
                file_id = parse_qs(parsed_url.query).get("id", [None])[0]
            elif "/d/" in url:
                file_id = url.split("/d/")[1].split("/")[0]
            if not file_id:
                raise ValueError("Could not extract file ID from URL.")
            filename = "".join(c if c.isalnum() else "_" for c in title) + ".pdf"
            filepath = os.path.join(output_dir, filename)
            print(f"⬇️  Downloading '{title}'...")
            success = download_file_from_google_drive(file_id, filepath)
            if not success:
                raise Exception("Download failed or file is not publicly accessible.")
        except Exception as e:
            print(f"⚠️ Failed to download {title}: {e}")
            print(f"🔗 Manual link: {url}\n")
    print("\n✅ All downloads attempted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download audio and transcripts from JSON mapping.")
    parser.add_argument("--audio_json", default="data/links.json", help="Path to links.json for audio download")
    parser.add_argument("--audio_out", default="data/audio_downloads", help="Output folder for audio files")
    parser.add_argument("--transcript_json", default="data/transcripts.json", help="Path to transcripts.json for transcript download")
    parser.add_argument("--pdf_out", default="data/transcript_downloads", help="Output folder for transcript PDFs")
    parser.add_argument("--mode", choices=["audio", "transcript", "both"], default="audio", help="Download mode")
    args = parser.parse_args()

    if args.mode in ("audio", "both"):
        download_audio_from_json(args.audio_json, args.audio_out)
    if args.mode in ("transcript", "both"):
        download_transcripts(args.transcript_json, args.pdf_out)