import os

transcript_dir = 'data/transcript_processed'

def clean_filename(filename):
    # Lowercase and remove spaces + underscores (but keep extension)
    name, ext = os.path.splitext(filename)
    cleaned = name.lower().replace(' ', '').replace('_', '') + ext
    return cleaned

def rename_transcript_files_in_dir(directory):
    for filename in os.listdir(directory):
        old_path = os.path.join(directory, filename)
        new_filename = clean_filename(filename)
        new_path = os.path.join(directory, new_filename)
        
        if old_path != new_path:
            os.rename(old_path, new_path)
            print(f"Renamed {filename} -> {new_filename}")

if __name__ == '__main__':

    print("Renaming transcript files...")
    rename_transcript_files_in_dir(transcript_dir)

    print("Done renaming transcript files!")