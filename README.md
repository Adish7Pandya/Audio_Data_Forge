# Advanced NPTEL Data Engineering Pipeline for ASR

This repository contains a fully automated data engineering pipeline built to create high-quality Speech-To-Text (STT) datasets from NPTEL courses. The pipeline handles everything from scraping and downloading to a multi-stage audio cleaning process, culminating in a dataset ready for training robust ASR models.

---

## 📊 Dashboard Overview

![Dashboard Screenshot](./06_dashboard/screenshots/dashboard_view_1.png)

### How to Launch the Dashboard

python 06_dashboard/app.py

---

## ✨ Key Features

- Fully Automated: A single command runs the entire pipeline from start to finish.
- Robust Scraping: Uses Playwright to effectively scrape YouTube video and PDF transcript links.
- Advanced Audio Cleaning:
    - Silence Removal: Automatically removes long pauses and silent segments.
    - Volume Normalization: Ensures consistent audio levels across all files.
    - Noise Reduction: Reduces background noise to improve signal quality.
- Text Normalization: Extracts and cleans text by lowercasing, removing punctuation, and converting numbers to words.
- ASR Manifest Generation: Creates a train_manifest.jsonl file, properly formatted for ASR frameworks.
- Visual Dashboard: Generates the static dashboard image summarizing the dataset.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

git clone https://github.com/Adish7Pandya/Ai4Bharat_Assignment.git
cd Ai4Bharat_Assignment

### 2. System Dependencies

- Python 3.8+
- FFmpeg:
    - Windows (Chocolatey): choco install ffmpeg
    - macOS (Homebrew): brew install ffmpeg
    - Ubuntu/Debian: sudo apt-get update && sudo apt-get install ffmpeg

### 3. Python Packages

pip install -r requirements.txt

### 4. Install Playwright Browsers

playwright install

---

## ▶️ How to Run the Pipeline

python main.py --url <YOUR_NPTEL_COURSE_URL>

### Example

python main.py --url https://nptel.ac.in/courses/106106184

---

## 🪜 Manual Step-by-Step Execution

# Step 1: Scrape Links
python 01_scraper/scrape_data.py --url <YOUR_NPTEL_COURSE_URL>
python 01_scraper/scrape_transcript.py --url <YOUR_NPTEL_COURSE_URL>

# Step 2: Download Audio and Transcripts
python 02_downloader/download_data.py

# Step 3: Preprocess and Clean Audio Files
python 03_audio_preprocessor/cleanse_audio.py
python 03_audio_preprocessor/normalize.py
python 03_audio_preprocessor/remove_trailing_audio.py
python 03_audio_preprocessor/rename_audio.py

# Step 4: Preprocess and Clean Text Transcripts
python 04_text_preprocessor/preprocess_transcript.py
python 04_text_preprocessor/rename_transcript.py

# Step 5: Create the Training Manifest
python 05_create_manifest/create_manifest.py

# Step 6: Generate the Dashboard Statistics
python 06_dashboard/process_data.py

---

## 🔬 Observations & Reflections on the Process

# Scraping
# Using Playwright is essential since NPTEL pages are dynamically loaded with JavaScript.

# Audio Processing
# Multi-stage audio cleaning:
# - Removes long silences
# - Reduces background noise
# - Normalizes volume

# Text Normalization
# Converts numbers to words, removes punctuation, lowercases text.

# Automation
# main.py orchestrates all steps for reproducibility.

---

## 📂 Data Overview

data/
├── links.json               # Scraped YouTube links
├── transcripts.json         # Scraped PDF transcript links
├── audio_downloads/         # Raw audio from YouTube
├── transcript_downloads/    # Raw PDF transcripts
├── audio_wav/               # Audio converted to .wav
├── audio_processed/         # Cleaned audio ready for ASR
├── transcript_processed/    # Cleaned and normalized .txt transcripts
└── train_manifest.jsonl     # Final output ready for ASR training

---

## 📁 Project Structure

.
├── main.py
├── scraper/
│   └── scrape_data.py
├── downloader/
│   └── download_data.py
├── audio_preprocessor/
│   ├── preprocess_audio.sh
│   ├── remove_trailing_audio.py
│   └── rename_files.py
├── text_preprocessor/
│   ├── preprocess_transcript.py
│   └── rename_files.py
├── train_manifest/
│   └── create_manifest.py
├── dashboard/
│   ├── process_data.py
│   └── dashboard_data.db
├── data/
│   ├── audio_downloads/
│   ├── audio_wav/
│   ├── audio_processed/
│   ├── transcript_downloads/
│   ├── transcript_processed/
│   ├── transcripts.json
│   └── video_links.json
├── requirements.txt
├── README.md
└── train_manifest.jsonl
