import os

audio_dir = 'data/audio_processed'

def clean_filename(filename):
    # Lowercase and remove spaces + underscores (but keep extension)
    name, ext = os.path.splitext(filename)
    cleaned = name.lower().replace(' ', '').replace('_', '').replace('-', '') + ext
    return cleaned

def rename_audio_files_in_dir(directory):
    for filename in os.listdir(directory):
        old_path = os.path.join(directory, filename)
        new_filename = clean_filename(filename)
        new_path = os.path.join(directory, new_filename)
        
        if old_path != new_path:
            os.rename(old_path, new_path)
            print(f"Renamed {filename} -> {new_filename}")

if __name__ == '__main__':
    print("Renaming audio files...")
    rename_audio_files_in_dir(audio_dir)
    print("Done renaming audio files.")