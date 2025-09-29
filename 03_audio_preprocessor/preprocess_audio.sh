#!/bin/bash

# Usage: ./preprocess_audio.sh <input_dir> <output_dir> <num_cpus>

input_dir=$1
output_dir=$2
num_cpus=$3

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Function to process a single file
process_file() {
    input_file="$1"
    filename=$(basename "$input_file")
    output_file="$output_dir/${filename%.*}.wav"

    echo "Processing $filename..."
    ffmpeg -y -i "$input_file" -ac 1 -ar 16000 "$output_file"
}

export -f process_file
export output_dir

# Make sure GNU parallel is installed
if ! command -v parallel &> /dev/null; then
    echo "Error: GNU parallel is not installed. Please run: sudo apt install parallel"
    exit 1
fi

# Find and process all audio files in parallel
find "$input_dir" -type f \( -iname "*.mp3" -o -iname "*.m4a" -o -iname "*.webm" -o -iname "*.wav" -o -iname "*.flac" \) | parallel -j "$num_cpus" process_file

