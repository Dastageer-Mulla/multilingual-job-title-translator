import pandas as pd
from lingua import Language, LanguageDetectorBuilder
from tqdm import tqdm

# 1. Setup Lingua
languages = [Language.ENGLISH, Language.ITALIAN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()


def analyze_data_quality(file_path):
    print(f"Loading {file_path}...")
    df = pd.read_csv(file_path)
    total_rows = len(df)

    # --- PART 1: DUPLICATE ANALYSIS ---
    print("Analyzing Duplicates...")
    # Exact duplicates (Both columns same)
    exact_duplicates = df.duplicated().sum()

    # Duplicate Search Terms (Same English, maybe different Italian)
    duplicate_searchterms = df.duplicated(subset=['searchterm']).sum()

    # Duplicate Italian Job Titles (Different English, same Italian)
    duplicate_translations = df.duplicated(subset=['italian_jobtitles']).sum()

    # Unique Pairs (The real size of your training data)
    unique_pairs_df = df.drop_duplicates(subset=['searchterm', 'italian_jobtitles'])
    unique_pairs_count = len(unique_pairs_df)

    # --- PART 2: LANGUAGE ANALYSIS ---
    same_language_count = 0
    different_language_count = 0
    uncertain_count = 0

    print("Analyzing Language Pairs...")
    for index, row in tqdm(df.iterrows(), total=total_rows):
        en_col = str(row['searchterm']).strip()
        it_col = str(row['italian_jobtitles']).strip()

        if en_col.lower() == it_col.lower():
            same_language_count += 1
            continue

        lang_searchterm = detector.detect_language_of(en_col)
        lang_italian_col = detector.detect_language_of(it_col)

        if lang_searchterm is None or lang_italian_col is None:
            uncertain_count += 1
        elif lang_searchterm == lang_italian_col:
            same_language_count += 1
        else:
            different_language_count += 1

    # --- FINAL REPORT ---
    print("\n" + "=" * 50)
    print("        FULL DATA QUALITY REPORT")
    print("=" * 50)
    print(f"Total Rows in File:         {total_rows}")

    print("\n--- DUPLICATE STATS ---")
    print(f"Exact Duplicate Rows:       {exact_duplicates} ({(exact_duplicates / total_rows) * 100:.2f}%)")
    print(f"Repeating Search Terms:     {duplicate_searchterms} ({(duplicate_searchterms / total_rows) * 100:.2f}%)")
    print(f"Repeating Italian Titles:   {duplicate_translations} ({(duplicate_translations / total_rows) * 100:.2f}%)")
    print(f"UNIQUE TRAINING PAIRS:      {unique_pairs_count}")

    print("\n--- LANGUAGE STATS ---")
    print(f"Same Language detected:     {same_language_count} ({(same_language_count / total_rows) * 100:.2f}%)")
    print(
        f"Different Lang detected:    {different_language_count} ({(different_language_count / total_rows) * 100:.2f}%)")
    print(f"Uncertain/Ambiguous:        {uncertain_count} ({(uncertain_count / total_rows) * 100:.2f}%)")
    print("=" * 50)

    # Recommendation
    if unique_pairs_count < total_rows * 0.8:
        print("ADVICE: You have many duplicates. Consider using 'df.drop_duplicates()' before fine-tuning.")
    else:
        print("ADVICE: Duplicate levels are acceptable for a dataset of this size.")
    print("=" * 50)


if __name__ == "__main__":
    analyze_data_quality("translated_jobtitles.csv")