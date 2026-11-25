import pandas as pd
import json
import os
import time
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from google import genai
from tqdm import tqdm

# --- CONFIGURATION ---
API_KEY = "AIzaSyCelgJpU2NAtRUzboiC6L-fgnlIdas5Vkk" # Replace with your actual key
MODEL_ID = "gemma-3-27b-it"
INPUT_FILE = "WJ Category Resolving Test Data 320K.csv"
OUTPUT_FILE = "translated_jobtitles_nl.csv" # Updated output file name
CHECKPOINT_FILE = "translation_progress_log_nl.csv" # Updated checkpoint file name

# --- COLUMN SETTINGS ---
SOURCE_COLUMN = "searchterm"

# --- BATCHING & THREADING ---
BATCH_SIZE = 50  # Items per API call
MAX_WORKERS = 5  # Number of parallel threads (Adjust based on your API limits)
MAX_RETRIES = 5
ROWS_TO_PROCESS_LIMIT = 20000

client = genai.Client(api_key=API_KEY)
csv_lock = threading.Lock()


# def get_pure_dutch_prompt(titles):
#     titles_str = "\n".join([f"- {t}" for t in titles])
#     return f"""
def get_realistic_dutch_prompt(titles):
    titles_str = "\n".join([f"- {t}" for t in titles])
    return f"""
### ROLE
Professional Dutch HR Specialist and Job Market Expert.

### OBJECTIVE
Standardize and translate these job titles into the natural terminology used on modern Dutch job portals (like Indeed.nl or LinkedIn Netherlands).

### RULES
1. TRANSLATE TRADITIONAL ROLES: Translate manual labor, healthcare, education, and standard roles into Dutch (e.g., "Nurse" -> "Verpleegkundige", "Carpenter" -> "Timmerman", "Teacher" -> "Docent").
2. KEEP ACCEPTED ENGLISH TERMS: The Dutch job market heavily uses English for IT, Corporate, and Modern roles. Keep these in English if it is the industry standard (e.g., keep "Data Scientist", "Account Manager", "HR Manager", "Front-end Developer").
3. FIX MESSY INPUT: Correct spelling mistakes and remove unnecessary symbols.
4. FORMAT: Return ONLY a JSON list of strings. No markdown formatting.

### INPUT:
{titles_str}

### JSON OUTPUT:
"""


def clean_json_response(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?', '', text)
        text = re.sub(r'```$', '', text)
    return text.strip()


def translate_batch(batch_list):
    retry_delay = 5
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=get_pure_dutch_prompt(batch_list),
                config={
                    'temperature': 0.0,
                    'response_mime_type': 'application/json' # Forces pure JSON output
                }
            )

            clean_text = clean_json_response(response.text)
            translated = json.loads(clean_text)

            if isinstance(translated, list) and len(translated) == len(batch_list):
                return translated
            else:
                print(f"\n[Warning] Batch size mismatch. Retrying...")
        except Exception as e:
            time.sleep(retry_delay)
            retry_delay *= 2

    return ["ERROR"] * len(batch_list)


def process_and_save_batch(batch_data, pbar):
    """Worker function for threads"""
    batch_titles = batch_data[SOURCE_COLUMN].tolist()
    results = translate_batch(batch_titles)

    batch_df = pd.DataFrame({
        SOURCE_COLUMN: batch_titles,
        'dutch_jobtitles': results # Updated column name to Dutch
    })

    # Thread-safe writing to CSV
    with csv_lock:
        batch_df.to_csv(CHECKPOINT_FILE, mode='a', index=False, header=False)

    pbar.update(len(batch_data))


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return

    # Load data and normalize headers
    df = pd.read_csv(INPUT_FILE)
    df.columns = [c.lower().strip() for c in df.columns]

    # Handle Checkpoint
    if os.path.exists(CHECKPOINT_FILE):
        processed_df = pd.read_csv(CHECKPOINT_FILE)
        start_idx = len(processed_df)
        print(f"Resuming from row {start_idx}...")
    else:
        start_idx = 0
        # Updated column name to Dutch
        pd.DataFrame(columns=[SOURCE_COLUMN, 'dutch_jobtitles']).to_csv(CHECKPOINT_FILE, index=False)

    # Define the range for this run
    end_idx = min(start_idx + ROWS_TO_PROCESS_LIMIT, len(df))
    rows_to_do = end_idx - start_idx

    if rows_to_do <= 0:
        print("All rows already processed or limit reached.")
        return

    print(f"Processing {rows_to_do} rows (From {start_idx} to {end_idx}) using {MAX_WORKERS} threads.")

    # Prepare batches
    batches = []
    for i in range(start_idx, end_idx, BATCH_SIZE):
        batches.append(df.iloc[i: min(i + BATCH_SIZE, end_idx)])

    # Threaded Execution
    with tqdm(total=rows_to_do, desc="Total Progress") as pbar:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Pass each batch to the executor
            futures = [executor.submit(process_and_save_batch, batch, pbar) for batch in batches]

            # Wait for all threads to finish
            for future in futures:
                future.result()

    # Final Save/Export
    final_df = pd.read_csv(CHECKPOINT_FILE)
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nDONE! {len(final_df)} rows now exist in {OUTPUT_FILE}")


if __name__ == "__main__":
    main()