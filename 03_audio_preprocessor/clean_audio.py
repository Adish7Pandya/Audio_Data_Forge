#!/usr/bin/env python3
"""
Audio Cleaning Pipeline:
1. Remove long silences
2. Normalize audio volume
3. Reduce background noise

Usage:
    python audio_preprocessor/clean_audio.py input_folder output_folder
"""

import os
import sys
from pydub import AudioSegment, silence, effects
import noisereduce as nr
import librosa
import soundfile as sf

# ---------- Step 1: Remove Long Silences ----------
def remove_silence(sound, min_silence_len=500, silence_thresh=-40):
    chunks = silence.split_on_silence(
        sound,
        min_silence_len=min_silence_len,
        silence_thresh=sound.dBFS + silence_thresh
    )
    processed = AudioSegment.empty()
    for chunk in chunks:
        processed += chunk + AudioSegment.silent(duration=100)  # add tiny pause
    return processed

# ---------- Step 2: Normalize Volume ----------
def normalize_volume(sound):
    return effects.normalize(sound)

# ---------- Step 3: Reduce Background Noise ----------
def reduce_noise(sound, sr=16000):
    # Convert pydub sound -> numpy
    samples = sound.get_array_of_samples()
    y = librosa.util.buf_to_float(samples, n_bytes=2)
    reduced = nr.reduce_noise(y=y, sr=sr)
    # Write back to AudioSegment
    temp_file = "temp_denoised.wav"
    sf.write(temp_file, reduced, sr)
    return AudioSegment.from_wav(temp_file)

# ---------- Main Processing Function ----------
def process_audio(input_path, output_path):
    try:
        sound = AudioSegment.from_wav(input_path)
        
        # Step 1: Remove silence
        sound = remove_silence(sound)
        
        # Step 2: Normalize
        sound = normalize_volume(sound)
        
        # Step 3: Noise reduction
        sound = reduce_noise(sound, sr=sound.frame_rate)
        
        # Export final file
        sound.export(output_path, format="wav")
        print(f"[✓] Processed: {input_path} -> {output_path}")
    except Exception as e:
        print(f"[!] Error processing {input_path}: {e}")

# ---------- Run Over Folder ----------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_audio.py <input_folder> <output_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".wav"):
            in_path = os.path.join(input_folder, filename)
            out_path = os.path.join(output_folder, filename)
            process_audio(in_path, out_path)
