import json
import re
from pathlib import Path
from collections import Counter


# ============================================================
# PATHS
# ============================================================

BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "vocabulary_profile.json"


# ============================================================
# LOAD MESSAGES
# ============================================================

def load_messages():
    if not INPUT_FILE.exists():
        print(f"ERROR: File not found: {INPUT_FILE}")
        return []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# TOKENIZE MESSAGE
# ============================================================

def tokenize(text):
    """
    Convert a message into individual words.
    """

    if not text:
        return []

    text = text.lower()

    # Extract words, including simple contractions
    words = re.findall(
        r"[a-zA-Z]+(?:'[a-zA-Z]+)?",
        text
    )

    return words


# ============================================================
# BUILD PROFILE
# ============================================================

def build_vocabulary_profile(messages):

    word_counter = Counter()

    total_messages = 0

    for message in messages:

        text = message.get("message")

        # Skip empty messages
        if not text:
            continue

        # Skip deleted messages
        if message.get("is_deleted") is True:
            continue

        # Skip media messages
        if message.get("is_media") is True:
            continue

        words = tokenize(text)

        if words:
            total_messages += 1
            word_counter.update(words)

    total_words = sum(word_counter.values())
    unique_words = len(word_counter)

    return {
        "total_messages_analyzed": total_messages,
        "total_words": total_words,
        "unique_words": unique_words,
        "top_words": [
            {
                "word": word,
                "count": count
            }
            for word, count in word_counter.most_common(20)
        ]
    }


# ============================================================
# SEPARATE SPEAKERS
# ============================================================

def separate_speakers(messages):

    speakers = {}

    for message in messages:

        sender = message.get("sender")

        # Ignore system messages
        if not sender:
            continue

        # Ignore messages without text
        if not message.get("message"):
            continue

        # Ignore deleted messages
        if message.get("is_deleted") is True:
            continue

        # Ignore media messages
        if message.get("is_media") is True:
            continue

        if sender not in speakers:
            speakers[sender] = []

        speakers[sender].append(message)

    return speakers


# ============================================================
# PRINT PROFILE
# ============================================================

def print_profile(speaker, profile):

    print()
    print("=" * 60)
    print(f"SPEAKER: {speaker}")
    print("=" * 60)

    print(
        f"Messages analyzed : "
        f"{profile['total_messages_analyzed']}"
    )

    print(
        f"Total words       : "
        f"{profile['total_words']}"
    )

    print(
        f"Unique words      : "
        f"{profile['unique_words']}"
    )

    print()
    print("Top 20 words:")
    print("-" * 40)

    for rank, item in enumerate(
        profile["top_words"],
        start=1
    ):
        print(
            f"{rank:2}. "
            f"{item['word']:<20} "
            f"{item['count']}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("DAY 4 - PER-SPEAKER VOCABULARY PROFILE")
    print("=" * 60)

    # Load data
    messages = load_messages()

    if not messages:
        print("No messages found.")
        return

    print(f"\nTotal records loaded: {len(messages)}")

    # Separate speakers
    speakers = separate_speakers(messages)

    print(f"Speakers found: {len(speakers)}")

    if not speakers:
        print("No speakers found.")
        return

    # Build profiles
    profiles = {}

    for speaker, speaker_messages in speakers.items():

        profile = build_vocabulary_profile(
            speaker_messages
        )

        profiles[speaker] = profile

        print_profile(
            speaker,
            profile
        )

    # Save result
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profiles,
            file,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 60)
    print("VOCABULARY PROFILE COMPLETE")
    print("=" * 60)

    print(f"\nSaved to:")
    print(OUTPUT_FILE)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()