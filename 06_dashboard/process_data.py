import sqlite3
import json
import os

# --- Configuration ---
# Path to your raw data file
INPUT_FILE = '../train_manifest.jsonl' 
# Path where the database will be created/updated
DB_FILE = 'dashboard_data.db'

def levenshtein_distance(s1, s2):
    """
    Calculates the Levenshtein distance between two sequences (e.g., words or characters).
    This distance is the minimum number of single-element edits (insertions, deletions, substitutions)
    required to change s1 into s2.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def process_manifest(input_file, db_file):
    """
    Processes a .jsonl manifest file to extract audio data metrics,
    calculates summary and error statistics, and saves everything to an SQLite database.
    """
    # --- Data Collection ---
    total_duration = 0
    total_utterances = 0
    vocabulary = set()
    alphabet = set()
    audio_data_rows = []

    # --- Variables for Error Calculation ---
    total_word_errors = 0
    total_ref_words = 0
    total_char_errors = 0
    total_ref_chars = 0
    sum_of_word_accuracies = 0.0

    print(f"Starting to process {input_file}...")
    
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at '{input_file}'.")
        print("Your project structure in the VS Code sidebar shows the file should be at this path.")
        print("Please double-check the path and the directory you are running the script from.")
        return

    # Read and process each line from the JSONL file
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            duration = data.get('duration', 0)
            ref_text = data.get('text', '')
            # IMPORTANT: Assumes a 'pred_text' field exists for the model's prediction
            pred_text = data.get('pred_text', '')
    
            # Update overall stats
            total_duration += duration
            total_utterances += 1
            vocabulary.update(ref_text.lower().split())
            alphabet.update(char for char in ref_text)

            # --- Calculate Errors for this Utterance ---
            ref_words = ref_text.split()
            pred_words = pred_text.split()
            
            word_errors = levenshtein_distance(ref_words, pred_words)
            char_errors = levenshtein_distance(list(ref_text), list(pred_text))

            num_ref_words = len(ref_words)
            num_ref_chars = len(ref_text)
            
            # Accumulate totals
            total_word_errors += word_errors
            total_ref_words += num_ref_words
            total_char_errors += char_errors
            total_ref_chars += num_ref_chars

            # Calculate accuracy for this specific utterance and add to sum
            if num_ref_words > 0:
                utterance_accuracy = (num_ref_words - word_errors) / num_ref_words
                sum_of_word_accuracies += utterance_accuracy

            # Append row for bulk insertion
            audio_data_rows.append((
                data.get('audio_filepath', ''), 
                duration, 
                len(ref_words), 
                len(ref_text)
            ))

    print("File processing complete.")

    # --- Calculate Final Metrics ---
    wer = (total_word_errors / total_ref_words) * 100 if total_ref_words > 0 else 0
    cer = (total_char_errors / total_ref_chars) * 100 if total_ref_chars > 0 else 0
    # Word Match Rate is often defined as 100 - WER.
    wmr = 100 - wer
    # Mean Word Accuracy is the average of individual utterance accuracies.
    mean_word_accuracy = (sum_of_word_accuracies / total_utterances) * 100 if total_utterances > 0 else 0


    # --- Database Interaction ---
    print(f"Connecting to database at {db_file}...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # --- Create/Recreate Tables ---
    cursor.execute("DROP TABLE IF EXISTS audio_data")
    cursor.execute("DROP TABLE IF EXISTS summary_statistics")
    print("Old tables dropped.")

    cursor.execute('''
    CREATE TABLE audio_data (
        audio_filepath TEXT,
        duration REAL,
        num_words INTEGER,
        num_characters INTEGER
    )
    ''')
    cursor.execute('''
    CREATE TABLE summary_statistics (
        total_duration REAL,
        total_utterances INTEGER,
        vocabulary_size INTEGER,
        alphabet_size INTEGER,
        alphabet TEXT,
        word_error_rate REAL,
        character_error_rate REAL,
        word_match_rate REAL,
        mean_word_accuracy REAL
    )
    ''')
    print("New tables created.")

    # --- Insert Data ---
    cursor.executemany('''
    INSERT INTO audio_data (audio_filepath, duration, num_words, num_characters)
    VALUES (?, ?, ?, ?)
    ''', audio_data_rows)
    print(f"{len(audio_data_rows)} rows inserted into 'audio_data'.")

    # Insert the single row of summary statistics with calculated values
    cursor.execute('''
    INSERT INTO summary_statistics (
        total_duration, total_utterances, vocabulary_size, alphabet_size, alphabet,
        word_error_rate, character_error_rate, word_match_rate, mean_word_accuracy
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        total_duration, total_utterances, len(vocabulary), len(alphabet), 
        ''.join(sorted(list(alphabet))), 
        wer, cer, wmr, mean_word_accuracy
    ))
    print("Summary statistics inserted.")

    conn.commit()
    conn.close()

    # --- Final Summary ---
    print("\n--- Summary ---")
    print(f"✅ Total Duration: {total_duration:.2f} seconds")
    print(f"✅ Total Utterances: {total_utterances}")
    print(f"✅ Vocabulary Size: {len(vocabulary)}")
    print(f"✅ Alphabet Size: {len(alphabet)}")
    print(f"✅ Alphabet: {''.join(sorted(alphabet))}")
    print(f"✅ Data saved to SQLite database: {db_file}")

if __name__ == "__main__":
    process_manifest(INPUT_FILE, DB_FILE)

