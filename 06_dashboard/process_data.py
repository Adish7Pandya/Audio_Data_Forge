import json
import csv
import string

#columns=> audio_filepath,duration,num_words,num_characters
#function returns  Total Hours, Total Utterances, Vocabulary Size,Alphabet Size ,Alphabet

import sqlite3
import json
import string

# Path to train_manifest.jsonl file
input_file = 'train_manifest.jsonl'
db_file = 'dashboard/dashboard_data.db'

# Function to process the manifest and save data to SQLite
def process_manifest(input_file, db_file):
    total_duration = 0
    total_utterances = 0
    vocabulary = set()
    alphabet = set()
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create tables for processed data and summary statistics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audio_data (
        audio_filepath TEXT,
        duration REAL,
        num_words INTEGER,
        num_characters INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS summary_statistics (
        total_duration REAL,
        total_utterances INTEGER,
        vocabulary_size INTEGER,
        alphabet_size INTEGER,
        alphabet TEXT
    )
    ''')
    cursor.execute("DELETE FROM audio_data")

    # Read and process the JSONL file
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            duration = data.get('duration', 0)
            text = data.get('text', '')
    
            alphabet.update(char for char in text.lower() if not char.isspace())
            total_duration += duration
            total_utterances += 1
            vocabulary.update(text.split())
    
            cursor.execute('''
            INSERT INTO audio_data (audio_filepath, duration, num_words, num_characters)
            VALUES (?, ?, ?, ?)
            ''', (data.get('audio_filepath', ''), duration, len(text.split()), len(text)))
    
    
    # Check if any rows exist in summary_statistics
    cursor.execute("SELECT COUNT(*) FROM summary_statistics")
    row_count = cursor.fetchone()[0]
    
    # If no rows exist, insert the first row, otherwise update
    if row_count == 0:
        cursor.execute('''
        INSERT INTO summary_statistics (total_duration, total_utterances, vocabulary_size, alphabet_size, alphabet)
        VALUES (?, ?, ?, ?, ?)
        ''', (total_duration, total_utterances, len(vocabulary), len(alphabet), ''.join(sorted(alphabet))))
    else:
        cursor.execute('''
        UPDATE summary_statistics
        SET total_duration = ?, 
            total_utterances = ?, 
            vocabulary_size = ?, 
            alphabet_size = ?, 
            alphabet = ?
        ''', (total_duration, total_utterances, len(vocabulary), len(alphabet), ''.join(sorted(alphabet))))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    # Print summary statistics
    print(f"✅ Total Hours: {total_duration / 3600:.2f}")
    print(f"✅ Total Utterances: {total_utterances}")
    print(f"✅ Vocabulary Size: {len(vocabulary)}")
    print(f"✅ Alphabet Size: {len(alphabet)}")
    print(f"✅ Alphabet: {''.join(sorted(alphabet))}")
    print("✅ Data saved to SQLite database:", db_file)
    

if __name__ == "__main__":
    process_manifest("train_manifest.jsonl", "dashboard/dashboard_data.db")

