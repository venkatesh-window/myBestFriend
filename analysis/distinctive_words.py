import json
import re
from pathlib import Path
from collections import Counter


# ============================================================
# PATHS
# ============================================================

BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "distinctive_words.json"


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
# LOAD DATA
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
# GET SPEAKER WORD COUNTS
# ============================================================

def build_speaker_counters(messages):

    speaker_counters = {}

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

        if sender not in speaker_counters:
            speaker_counters[sender] = Counter()

        words = tokenize(text)

        speaker_counters[sender].update(words)

    return speaker_counters


# ============================================================
# CALCULATE DISTINCTIVENESS
# ============================================================

def calculate_distinctive_words(
    speaker_counters,
    top_n=30
):

    speakers = list(speaker_counters.keys())

    if len(speakers) < 2:

        print("ERROR: Need at least two speakers.")

        return {}

    results = {}

    total_words = {
        speaker: sum(counter.values())
        for speaker, counter
        in speaker_counters.items()
    }

    for speaker in speakers:

        other_speakers = [
            s for s in speakers
            if s != speaker
        ]

        counter = speaker_counters[speaker]

        distinctive = []

        for word, count in counter.items():

            speaker_frequency = (
                count /
                total_words[speaker]
            )

            other_count = sum(
                speaker_counters[other].get(
                    word,
                    0
                )
                for other in other_speakers
            )

            other_total = sum(
                total_words[other]
                for other in other_speakers
            )

            if other_total == 0:
                continue

            other_frequency = (
                other_count /
                other_total
            )

            # Add smoothing to avoid division by zero
            score = (
                (speaker_frequency + 1e-9)
                /
                (other_frequency + 1e-9)
            )

            distinctive.append(
                {
                    "word": word,
                    "count": count,
                    "speaker_frequency": round(
                        speaker_frequency,
                        8
                    ),
                    "other_frequency": round(
                        other_frequency,
                        8
                    ),
                    "distinctiveness_score": round(
                        score,
                        4
                    )
                }
            )

        distinctive.sort(
            key=lambda x:
            x["distinctiveness_score"],
            reverse=True
        )

        results[speaker] = distinctive[:top_n]

    return results


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(results):

    for speaker, words in results.items():

        print()
        print("=" * 65)
        print(f"DISTINCTIVE WORDS: {speaker}")
        print("=" * 65)

        print(
            f"{'Rank':<6}"
            f"{'Word':<20}"
            f"{'Count':<10}"
            f"{'Score':<10}"
        )

        print("-" * 65)

        for rank, item in enumerate(
            words,
            start=1
        ):

            print(
                f"{rank:<6}"
                f"{item['word']:<20}"
                f"{item['count']:<10}"
                f"{item['distinctiveness_score']:<10}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print("DAY 4 - DISTINCTIVE WORD RANKING")
    print("=" * 65)

    messages = load_messages()

    if not messages:
        return

    print(
        f"\nTotal records loaded: "
        f"{len(messages)}"
    )

    speaker_counters = (
        build_speaker_counters(messages)
    )

    print(
        f"Speakers found: "
        f"{len(speaker_counters)}"
    )

    for speaker, counter in speaker_counters.items():

        print(
            f"{speaker}: "
            f"{sum(counter.values())} words"
        )

    results = calculate_distinctive_words(
        speaker_counters,
        top_n=30
    )

    if not results:
        return

    print_results(results)

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
    print("=" * 65)
    print("DISTINCTIVE WORD ANALYSIS COMPLETE")
    print("=" * 65)

    print(f"\nSaved to:")
    print(OUTPUT_FILE)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()