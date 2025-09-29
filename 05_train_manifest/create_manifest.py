import json
import os
from pathlib import Path
import soundfile as sf

def get_audio_duration(audio_path):
    """
    Get the duration of a .wav audio file in seconds.
    """
    with sf.SoundFile(audio_path) as audio:
        duration = len(audio) / audio.samplerate
    return duration

def create_training_manifest():
    """
    Creates a train_manifest.jsonl file with audio_filepath, duration, and text.
    """
    # Define your paths
    AUDIO_DIR = 'data/audio_processed'
    TRANSCRIPT_DIR = 'data/transcript_processed'
    MANIFEST_PATH = 'train_manifest.jsonl'
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as manifest_file:
        for audio_file in os.listdir(AUDIO_DIR):
            if audio_file.endswith('.wav'):
                audio_path = os.path.join(AUDIO_DIR, audio_file)
                
                # Base filename (no extension)
                base_name = Path(audio_file).stem
                
                # Transcript path
                transcript_file = os.path.join(TRANSCRIPT_DIR, f'{base_name}.txt')
                
                if not os.path.isfile(transcript_file):
                    print(f"⚠️ Warning: No matching transcript for {audio_file}")
                    continue
                
                # Get text
                with open(transcript_file, 'r', encoding='utf-8') as tf:
                    text = tf.read().strip()
                
                # Get duration
                duration = get_audio_duration(audio_path)
                
                # Build JSON object
                entry = {
                    'audio_filepath': audio_path,
                    'duration': duration,
                    'text': text
                }
                
                # Write JSON line
                manifest_file.write(json.dumps(entry) + '\n')
                print(f"✅ Added {audio_file} to manifest.")

    print(f"\n Manifest created at {MANIFEST_PATH}")

if __name__ == '__main__':
    create_training_manifest()
    print("Manifest creation complete.")


