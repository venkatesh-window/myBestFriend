import json
import re
from pathlib import Path
from collections import Counter


# ============================================================
# PATHS
# ============================================================

BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "common_vs_distinctive.json"


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
# BUILD SPEAKER WORD COUNTS
# ============================================================

def build_speaker_counts(messages):

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
            speakers[sender] = Counter()

        words = tokenize(text)

        speakers[sender].update(words)

    return speakers


# ============================================================
# CLASSIFY WORDS
# ============================================================

def classify_words(
    speaker_counts,
    minimum_count=3
):

    speakers = list(speaker_counts.keys())

    if len(speakers) < 2:

        print("ERROR: Need at least two speakers.")

        return {}

    speaker_a = speakers[0]
    speaker_b = speakers[1]

    counter_a = speaker_counts[speaker_a]
    counter_b = speaker_counts[speaker_b]

    # Words used by both speakers
    common_words = []

    # Words used primarily by A
    speaker_a_words = []

    # Words used primarily by B
    speaker_b_words = []

    all_words = (
        set(counter_a.keys())
        |
        set(counter_b.keys())
    )

    for word in all_words:

        count_a = counter_a.get(word, 0)
        count_b = counter_b.get(word, 0)

        total = count_a + count_b

        # Ignore extremely rare words
        if total < minimum_count:
            continue

        # ----------------------------------------------------
        # COMMON
        # ----------------------------------------------------

        if count_a > 0 and count_b > 0:

            common_words.append(
                {
                    "word": word,
                    "total_count": total,
                    speaker_a: count_a,
                    speaker_b: count_b
                }
            )

        # ----------------------------------------------------
        # SPEAKER A
        # ----------------------------------------------------

        elif count_a > 0:

            speaker_a_words.append(
                {
                    "word": word,
                    "count": count_a
                }
            )

        # ----------------------------------------------------
        # SPEAKER B
        # ----------------------------------------------------

        elif count_b > 0:

            speaker_b_words.append(
                {
                    "word": word,
                    "count": count_b
                }
            )

    # Sort
    common_words.sort(
        key=lambda x: x["total_count"],
        reverse=True
    )

    speaker_a_words.sort(
        key=lambda x: x["count"],
        reverse=True
    )

    speaker_b_words.sort(
        key=lambda x: x["count"],
        reverse=True
    )

    return {
        "common_words": common_words,
        speaker_a: speaker_a_words,
        speaker_b: speaker_b_words
    }


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(
    results,
    speaker_a,
    speaker_b
):

    print()
    print("=" * 75)
    print("COMMON VS DISTINCTIVE VOCABULARY")
    print("=" * 75)

    # --------------------------------------------------------
    # COMMON
    # --------------------------------------------------------

    common = results["common_words"]

    print()
    print("=" * 75)
    print("COMMON VOCABULARY")
    print("=" * 75)

    print(
        f"{'Rank':<6}"
        f"{'Word':<20}"
        f"{speaker_a:<20}"
        f"{speaker_b:<20}"
    )

    print("-" * 75)

    for rank, item in enumerate(
        common[:30],
        start=1
    ):

        print(
            f"{rank:<6}"
            f"{item['word']:<20}"
            f"{item[speaker_a]:<20}"
            f"{item[speaker_b]:<20}"
        )

    # --------------------------------------------------------
    # SPEAKER A
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print(f"DISTINCTIVE TO: {speaker_a}")
    print("=" * 75)

    for rank, item in enumerate(
        results[speaker_a][:30],
        start=1
    ):

        print(
            f"{rank:<6}"
            f"{item['word']:<20}"
            f"{item['count']}"
        )

    # --------------------------------------------------------
    # SPEAKER B
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print(f"DISTINCTIVE TO: {speaker_b}")
    print("=" * 75)

    for rank, item in enumerate(
        results[speaker_b][:30],
        start=1
    ):

        print(
            f"{rank:<6}"
            f"{item['word']:<20}"
            f"{item['count']}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)
    print("DAY 4 - COMMON VS DISTINCTIVE VOCABULARY")
    print("=" * 75)

    messages = load_messages()

    if not messages:
        return

    print(
        f"\nTotal records loaded: "
        f"{len(messages)}"
    )

    speaker_counts = (
        build_speaker_counts(messages)
    )

    speakers = list(speaker_counts.keys())

    print(
        f"Speakers found: "
        f"{len(speakers)}"
    )

    if len(speakers) < 2:
        return

    results = classify_words(
        speaker_counts,
        minimum_count=3
    )

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
    print("COMMON VS DISTINCTIVE ANALYSIS COMPLETE")
    print("=" * 75)

    print("\nSaved to:")
    print(OUTPUT_FILE)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()