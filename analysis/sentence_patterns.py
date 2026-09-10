import json
import re
from pathlib import Path
from collections import Counter


BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "sentence_patterns.json"


# ---------------------------------------------------------
# LOAD MESSAGES
# ---------------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# ---------------------------------------------------------
# SENTENCE SEGMENTATION
# ---------------------------------------------------------

def split_sentences(text):
    """
    Split a message into sentences using:
    . ! ? and their repeated forms.
    """

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    # Split after sentence-ending punctuation
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # Remove empty pieces
    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    return sentences


# ---------------------------------------------------------
# WORD COUNT
# ---------------------------------------------------------

def count_words(text):
    """
    Count words using a simple alphabetic tokenizer.
    """

    words = re.findall(
        r"[A-Za-z]+(?:'[A-Za-z]+)?",
        text
    )

    return len(words)


# ---------------------------------------------------------
# SPEAKER DATA
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

    # Create speaker profile
    if sender not in speaker_data:
        speaker_data[sender] = {
            "messages_analyzed": 0,
            "sentences": [],
            "sentence_lengths": [],
            "messages_with_multiple_sentences": 0,
            "messages_with_single_sentence": 0,
        }

    data = speaker_data[sender]

    data["messages_analyzed"] += 1

    # Split message into sentences
    sentences = split_sentences(text)

    if not sentences:
        continue

    # Store sentence information
    for sentence in sentences:

        word_count = count_words(sentence)

        if word_count == 0:
            continue

        data["sentences"].append(sentence)
        data["sentence_lengths"].append(word_count)

    # Single vs multiple sentence message
    if len(sentences) == 1:
        data["messages_with_single_sentence"] += 1

    else:
        data["messages_with_multiple_sentences"] += 1


# ---------------------------------------------------------
# BUILD FINAL PROFILE
# ---------------------------------------------------------

profile = {}


for speaker, data in speaker_data.items():

    sentence_lengths = data["sentence_lengths"]

    total_sentences = len(sentence_lengths)

    if total_sentences > 0:

        total_words = sum(sentence_lengths)

        average_sentence_length = (
            total_words / total_sentences
        )

        shortest_sentence = min(sentence_lengths)
        longest_sentence = max(sentence_lengths)

    else:

        total_words = 0
        average_sentence_length = 0
        shortest_sentence = 0
        longest_sentence = 0

    # Sentence length distribution
    distribution = Counter(sentence_lengths)

    sentence_length_distribution = {
        str(length): count
        for length, count in sorted(distribution.items())
    }

    # Percentage of messages containing multiple sentences
    total_messages = data["messages_analyzed"]

    if total_messages > 0:
        multi_sentence_percentage = (
            data["messages_with_multiple_sentences"]
            / total_messages
        ) * 100

    else:
        multi_sentence_percentage = 0

    profile[speaker] = {
        "messages_analyzed": total_messages,

        "total_sentences": total_sentences,

        "total_sentence_words": total_words,

        "average_sentence_length": round(
            average_sentence_length,
            2
        ),

        "shortest_sentence_words": shortest_sentence,

        "longest_sentence_words": longest_sentence,

        "messages_with_single_sentence":
            data["messages_with_single_sentence"],

        "messages_with_multiple_sentences":
            data["messages_with_multiple_sentences"],

        "multi_sentence_message_percentage": round(
            multi_sentence_percentage,
            2
        ),

        "sentence_length_distribution":
            sentence_length_distribution,
    }


# ---------------------------------------------------------
# SAVE RESULT
# ---------------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        profile,
        file,
        ensure_ascii=False,
        indent=2
    )


# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------

print("\n========== SENTENCE PATTERNS ==========\n")


for speaker, data in profile.items():

    print(f"Speaker: {speaker}")

    print(
        f"  Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print(
        f"  Total sentences: "
        f"{data['total_sentences']}"
    )

    print(
        f"  Average sentence length: "
        f"{data['average_sentence_length']} words"
    )

    print(
        f"  Shortest sentence: "
        f"{data['shortest_sentence_words']} words"
    )

    print(
        f"  Longest sentence: "
        f"{data['longest_sentence_words']} words"
    )

    print(
        f"  Single-sentence messages: "
        f"{data['messages_with_single_sentence']}"
    )

    print(
        f"  Multi-sentence messages: "
        f"{data['messages_with_multiple_sentences']}"
    )

    print(
        f"  Multi-sentence percentage: "
        f"{data['multi_sentence_message_percentage']}%"
    )

    print("\n")


print("Saved to:")
print(OUTPUT_FILE)