import json
import re
from pathlib import Path
from collections import Counter

INPUT_FILE = Path("data/processed/messages.json")

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# -----------------------------
# Language detection
# -----------------------------

def detect_language(text):
    if not text:
        return "empty"

    tamil_chars = re.findall(r"[\u0B80-\u0BFF]", text)
    english_chars = re.findall(r"[A-Za-z]", text)

    tamil_count = len(tamil_chars)
    english_count = len(english_chars)

    if tamil_count > 0 and english_count > 0:
        return "mixed"

    if tamil_count > 0:
        return "tamil"

    if english_count > 0:
        return "english"

    return "other"


stats = {}

senders = set(
    message["sender"]
    for message in messages
    if message.get("sender")
)

for sender in senders:

    sender_messages = [
        message
        for message in messages
        if message.get("sender") == sender
    ]

    language_counts = Counter()

    total_words = 0
    total_chars = 0

    for message in sender_messages:

        text = message.get("message", "")

        language = detect_language(text)

        language_counts[language] += 1

        total_chars += len(text)

        words = re.findall(r"\b[\w']+\b", text)
        total_words += len(words)

    stats[sender] = {
        "total_messages": len(sender_messages),
        "language_distribution": dict(language_counts),
        "total_words": total_words,
        "total_characters": total_chars
    }


# -----------------------------
# Print results
# -----------------------------

print("\n========== LANGUAGE ANALYSIS ==========\n")

for sender, data in stats.items():

    print(sender)

    print(f"  Messages: {data['total_messages']}")
    print(f"  Words: {data['total_words']}")
    print(f"  Characters: {data['total_characters']}")

    print("  Language distribution:")

    for language, count in data["language_distribution"].items():

        percentage = (
            count / data["total_messages"] * 100
            if data["total_messages"]
            else 0
        )

        print(
            f"    {language}: "
            f"{count} ({percentage:.2f}%)"
        )

    print()


# -----------------------------
# Save results
# -----------------------------

OUTPUT_FILE = Path("data/processed/language_analysis.json")

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(
        stats,
        file,
        ensure_ascii=False,
        indent=2
    )

print(f"Saved to: {OUTPUT_FILE}")