import json
import re
from pathlib import Path
from collections import Counter


# ============================================================
# PATHS
# ============================================================

BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "repeated_expressions.json"


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
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    # Keep letters, numbers and apostrophes
    text = re.sub(
        r"[^a-zA-Z0-9'\s]",
        " ",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# TOKENIZE
# ============================================================

def tokenize(text):

    text = normalize_text(text)

    if not text:
        return []

    return text.split()


# ============================================================
# CREATE N-GRAMS
# ============================================================

def create_ngrams(words, n):

    phrases = []

    if len(words) < n:
        return phrases

    for i in range(
        len(words) - n + 1
    ):

        phrase = " ".join(
            words[i:i + n]
        )

        phrases.append(phrase)

    return phrases


# ============================================================
# BUILD SPEAKER EXPRESSIONS
# ============================================================

def build_expressions(messages):

    expression_counts = Counter()

    expression_messages = Counter()

    for message in messages:

        text = message.get("message")

        if not text:
            continue

        if message.get("is_deleted") is True:
            continue

        if message.get("is_media") is True:
            continue

        words = tokenize(text)

        if not words:
            continue

        # 2-word expressions
        bigrams = create_ngrams(
            words,
            2
        )

        # 3-word expressions
        trigrams = create_ngrams(
            words,
            3
        )

        expressions = (
            bigrams +
            trigrams
        )

        # Count expression occurrences
        expression_counts.update(
            expressions
        )

        # Count number of messages
        # containing each expression only once
        unique_expressions = set(
            expressions
        )

        expression_messages.update(
            unique_expressions
        )

    return (
        expression_counts,
        expression_messages
    )


# ============================================================
# FILTER EXPRESSIONS
# ============================================================

def get_repeated_expressions(
    expression_counts,
    expression_messages,
    minimum_occurrences=3
):

    results = []

    for expression, count in expression_counts.items():

        # Ignore expressions that occur
        # only once or twice
        if count < minimum_occurrences:
            continue

        results.append(
            {
                "expression": expression,
                "occurrences": count,
                "messages_used_in": (
                    expression_messages[expression]
                )
            }
        )

    # Most frequently repeated first
    results.sort(
        key=lambda x: (
            x["occurrences"],
            x["messages_used_in"]
        ),
        reverse=True
    )

    return results


# ============================================================
# PROCESS ALL SPEAKERS
# ============================================================

def process_speakers(messages):

    speakers = {}

    for message in messages:

        sender = message.get("sender")

        if not sender:
            continue

        if not message.get("message"):
            continue

        if message.get("is_deleted") is True:
            continue

        if message.get("is_media") is True:
            continue

        if sender not in speakers:
            speakers[sender] = []

        speakers[sender].append(message)

    results = {}

    for speaker, speaker_messages in speakers.items():

        counts, message_counts = (
            build_expressions(
                speaker_messages
            )
        )

        results[speaker] = (
            get_repeated_expressions(
                counts,
                message_counts
            )
        )

    return results


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(results):

    for speaker, expressions in results.items():

        print()
        print("=" * 75)
        print(f"REPEATED PERSONAL EXPRESSIONS: {speaker}")
        print("=" * 75)

        if not expressions:

            print("No repeated expressions found.")

            continue

        print(
            f"{'Rank':<6}"
            f"{'Expression':<40}"
            f"{'Occurrences':<15}"
            f"{'Messages':<10}"
        )

        print("-" * 75)

        for rank, item in enumerate(
            expressions[:30],
            start=1
        ):

            print(
                f"{rank:<6}"
                f"{item['expression'][:38]:<40}"
                f"{item['occurrences']:<15}"
                f"{item['messages_used_in']:<10}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)
    print("DAY 4 - REPEATED PERSONAL EXPRESSIONS")
    print("=" * 75)

    messages = load_messages()

    if not messages:
        return

    print(
        f"\nTotal records loaded: "
        f"{len(messages)}"
    )

    results = process_speakers(
        messages
    )

    print(
        f"Speakers found: "
        f"{len(results)}"
    )

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
    print("=" * 75)
    print("REPEATED EXPRESSION ANALYSIS COMPLETE")
    print("=" * 75)

    print("\nSaved to:")
    print(OUTPUT_FILE)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()