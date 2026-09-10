import json
import re
from pathlib import Path
from collections import Counter, defaultdict


# ============================================================
# PATHS
# ============================================================

BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "word_frequency_ratios.json"


# ============================================================
# TOKENIZE
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
# BUILD WORD COUNTS
# ============================================================

def build_word_counts(messages):

    speaker_counts = defaultdict(Counter)

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

        words = tokenize(text)

        speaker_counts[sender].update(words)

    return speaker_counts


# ============================================================
# CALCULATE RATIOS
# ============================================================

def calculate_ratios(speaker_counts):

    speakers = list(speaker_counts.keys())

    if len(speakers) < 2:

        print("ERROR: Need at least two speakers.")

        return {}

    # Currently designed for two speakers
    speaker_a = speakers[0]
    speaker_b = speakers[1]

    all_words = (
        set(speaker_counts[speaker_a])
        |
        set(speaker_counts[speaker_b])
    )

    results = {}

    for word in all_words:

        count_a = speaker_counts[speaker_a].get(
            word,
            0
        )

        count_b = speaker_counts[speaker_b].get(
            word,
            0
        )

        total = count_a + count_b

        if total == 0:
            continue

        percentage_a = (
            count_a / total
        ) * 100

        percentage_b = (
            count_b / total
        ) * 100

        results[word] = {

            "total_count": total,

            speaker_a: {
                "count": count_a,
                "percentage": round(
                    percentage_a,
                    2
                )
            },

            speaker_b: {
                "count": count_b,
                "percentage": round(
                    percentage_b,
                    2
                )
            }
        }

    return results


# ============================================================
# PRINT MOST SPEAKER-SPECIFIC WORDS
# ============================================================

def print_results(results, speaker_a, speaker_b):

    print()
    print("=" * 75)
    print("WORD-FREQUENCY RATIOS")
    print("=" * 75)

    print()
    print(
        f"{'Word':<20}"
        f"{speaker_a:<20}"
        f"{speaker_b:<20}"
        f"{'Total':<10}"
    )

    print("-" * 75)

    # Sort by how strongly the word belongs to either speaker
    ranked = sorted(
        results.items(),
        key=lambda item: max(
            item[1][speaker_a]["percentage"],
            item[1][speaker_b]["percentage"]
        ),
        reverse=True
    )

    shown = 0

    for word, data in ranked:

        # Ignore extremely rare words for display
        if data["total_count"] < 5:
            continue

        a_percentage = (
            data[speaker_a]["percentage"]
        )

        b_percentage = (
            data[speaker_b]["percentage"]
        )

        print(
            f"{word:<20}"
            f"{a_percentage:>6.2f}% "
            f"({data[speaker_a]['count']:<5})   "
            f"{b_percentage:>6.2f}% "
            f"({data[speaker_b]['count']:<5})   "
            f"{data['total_count']:<10}"
        )

        shown += 1

        if shown >= 30:
            break


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)
    print("DAY 4 - SPEAKER WORD-FREQUENCY RATIOS")
    print("=" * 75)

    messages = load_messages()

    if not messages:
        return

    print(
        f"\nTotal records loaded: "
        f"{len(messages)}"
    )

    speaker_counts = build_word_counts(
        messages
    )

    speakers = list(speaker_counts.keys())

    print(
        f"Speakers found: "
        f"{len(speakers)}"
    )

    if len(speakers) < 2:
        return

    for speaker in speakers:

        total_words = sum(
            speaker_counts[speaker].values()
        )

        print(
            f"{speaker}: "
            f"{total_words} words"
        )

    results = calculate_ratios(
        speaker_counts
    )

    if not results:
        return

    print_results(
        results,
        speakers[0],
        speakers[1]
    )

    # Save
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
    print("=" * 75)
    print("WORD-FREQUENCY RATIO ANALYSIS COMPLETE")
    print("=" * 75)

    print("\nSaved to:")
    print(OUTPUT_FILE)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()