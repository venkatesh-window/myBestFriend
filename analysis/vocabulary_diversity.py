import json
import re
from pathlib import Path
from collections import Counter


# ============================================================
# PATHS
# ============================================================

BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "vocabulary_diversity.json"


# ============================================================
# TOKENIZER
# ============================================================

def tokenize(text):

    if not text:
        return []

    text = text.lower()

    return re.findall(
        r"[a-zA-Z]+(?:'[a-zA-Z]+)?",
        text
    )


# ============================================================
# LOAD MESSAGES
# ============================================================

def load_messages():

    if not INPUT_FILE.exists():

        print(f"ERROR: File not found: {INPUT_FILE}")

        return []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# GROUP MESSAGES BY SPEAKER
# ============================================================

def group_by_speaker(messages):

    speakers = {}

    for message in messages:

        sender = message.get("sender")
        text = message.get("message")

        if not sender:
            continue

        if not text:
            continue

        if message.get("is_deleted") is True:
            continue

        if message.get("is_media") is True:
            continue

        if sender not in speakers:
            speakers[sender] = []

        speakers[sender].append(text)

    return speakers


# ============================================================
# CALCULATE DIVERSITY
# ============================================================

def calculate_diversity(messages):

    all_words = []

    for message in messages:

        words = tokenize(message)

        all_words.extend(words)

    total_words = len(all_words)

    unique_words = len(set(all_words))

    # Type-Token Ratio
    if total_words > 0:
        ttr = unique_words / total_words
    else:
        ttr = 0

    # Percentage of unique vocabulary
    vocabulary_percentage = ttr * 100

    # Hapax legomena = words appearing only once
    counter = Counter(all_words)

    words_used_once = sum(
        1
        for count in counter.values()
        if count == 1
    )

    return {
        "total_words": total_words,
        "unique_words": unique_words,
        "type_token_ratio": round(ttr, 4),
        "vocabulary_diversity_percentage": round(
            vocabulary_percentage,
            2
        ),
        "words_used_once": words_used_once
    }


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(results):

    print()
    print("=" * 70)
    print("VOCABULARY DIVERSITY")
    print("=" * 70)

    for speaker, data in results.items():

        print()
        print("-" * 70)
        print(f"SPEAKER: {speaker}")
        print("-" * 70)

        print(
            f"Total words                  : "
            f"{data['total_words']}"
        )

        print(
            f"Unique words                 : "
            f"{data['unique_words']}"
        )

        print(
            f"Type-Token Ratio (TTR)       : "
            f"{data['type_token_ratio']}"
        )

        print(
            f"Vocabulary diversity         : "
            f"{data['vocabulary_diversity_percentage']}%"
        )

        print(
            f"Words used only once         : "
            f"{data['words_used_once']}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("DAY 4 - VOCABULARY DIVERSITY")
    print("=" * 70)

    messages = load_messages()

    if not messages:
        return

    print(
        f"\nTotal records loaded: "
        f"{len(messages)}"
    )

    speakers = group_by_speaker(messages)

    print(
        f"Speakers found: "
        f"{len(speakers)}"
    )

    results = {}

    for speaker, speaker_messages in speakers.items():

        results[speaker] = calculate_diversity(
            speaker_messages
        )

    print_results(results)

    # Save results
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print("VOCABULARY DIVERSITY ANALYSIS COMPLETE")
    print("=" * 70)

    print("\nSaved to:")
    print(OUTPUT_FILE)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()