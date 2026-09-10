import json
from pathlib import Path
from collections import Counter


BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "message_length_patterns.json"


# ---------------------------------------------------------
# LOAD MESSAGES
# ---------------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------

def count_words(text):
    words = text.split()
    return len(words)


# ---------------------------------------------------------
# ANALYZE
# ---------------------------------------------------------

speaker_data = {}


for message in messages:

    sender = message.get("sender")
    text = message.get("message")

    # Ignore system messages
    if not sender:
        continue

    # Ignore deleted messages
    if message.get("is_deleted"):
        continue

    # Ignore media-only messages
    if message.get("is_media"):
        continue

    if not text:
        continue

    text = text.strip()

    if not text:
        continue

    word_count = count_words(text)
    character_count = len(text)

    if sender not in speaker_data:
        speaker_data[sender] = {
            "messages_analyzed": 0,
            "word_counts": [],
            "character_counts": [],
        }

    speaker_data[sender]["messages_analyzed"] += 1
    speaker_data[sender]["word_counts"].append(word_count)
    speaker_data[sender]["character_counts"].append(character_count)


# ---------------------------------------------------------
# BUILD PROFILE
# ---------------------------------------------------------

profile = {}


for speaker, data in speaker_data.items():

    word_counts = data["word_counts"]
    character_counts = data["character_counts"]

    total_messages = len(word_counts)

    # Average
    average_words = (
        sum(word_counts) / total_messages
        if total_messages
        else 0
    )

    average_characters = (
        sum(character_counts) / total_messages
        if total_messages
        else 0
    )

    # Distribution
    word_distribution = Counter(word_counts)

    # Message categories
    very_short = sum(
        1 for count in word_counts
        if count <= 3
    )

    short = sum(
        1 for count in word_counts
        if 4 <= count <= 10
    )

    medium = sum(
        1 for count in word_counts
        if 11 <= count <= 30
    )

    long = sum(
        1 for count in word_counts
        if 31 <= count <= 60
    )

    very_long = sum(
        1 for count in word_counts
        if count > 60
    )

    profile[speaker] = {

        "messages_analyzed": total_messages,

        "average_words_per_message": round(
            average_words,
            2
        ),

        "average_characters_per_message": round(
            average_characters,
            2
        ),

        "shortest_message_words": min(word_counts)
        if word_counts else 0,

        "longest_message_words": max(word_counts)
        if word_counts else 0,

        "message_length_distribution": {
            str(length): count
            for length, count
            in sorted(word_distribution.items())
        },

        "message_categories": {

            "very_short_1_to_3_words": very_short,

            "short_4_to_10_words": short,

            "medium_11_to_30_words": medium,

            "long_31_to_60_words": long,

            "very_long_61_plus_words": very_long,
        },
    }


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        profile,
        file,
        ensure_ascii=False,
        indent=2
    )


# ---------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------

print("\n========== MESSAGE LENGTH PATTERNS ==========\n")


for speaker, data in profile.items():

    print(f"Speaker: {speaker}")

    print(
        f"  Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print(
        f"  Average words/message: "
        f"{data['average_words_per_message']}"
    )

    print(
        f"  Average characters/message: "
        f"{data['average_characters_per_message']}"
    )

    print(
        f"  Shortest message: "
        f"{data['shortest_message_words']} words"
    )

    print(
        f"  Longest message: "
        f"{data['longest_message_words']} words"
    )

    print("\n  Message categories:")

    for category, count in data["message_categories"].items():

        print(
            f"    {category}: {count}"
        )

    print("\n")


print("Saved to:")
print(OUTPUT_FILE)