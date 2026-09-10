import json
import re
from pathlib import Path
from collections import Counter

INPUT_FILE = Path("data/processed/messages.json")

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# -----------------------------------
# Basic Tanglish vocabulary
# -----------------------------------

TANGLISH_WORDS = {
    "enna", "epdi", "eppadi", "iruka", "irukku", "iruken",
    "irukinga", "illa", "illai", "venum", "vendam",
    "pannu", "panra", "panren", "pannitu", "pannunga",
    "poren", "pora", "poita", "poiten", "vandha",
    "vandhuta", "varuven", "vara", "varra",
    "saptiya", "sapten", "sapti", "saptacha",
    "romba", "konjam", "seri", "sari", "apdi",
    "ipdi", "inga", "anga", "enga", "yenga",
    "evlo", "yen", "eppo", "ippo", "naala",
    "nethu", "innaiku", "tomorrow", "theriyuma",
    "therila", "puriyala", "purinjitha", "aama",
    "ama", "ok", "paravala", "paakalam", "polam",
    "va", "vaa", "po", "poi", "sollu", "sonna",
    "solla", "kudunga", "kudu", "eduthu", "vechuko"
}


def get_words(text):
    return re.findall(r"[A-Za-z]+", text.lower())


def count_tanglish_words(text):
    words = get_words(text)

    return sum(
        1 for word in words
        if word in TANGLISH_WORDS
    )


def detect_language(text):

    if not text.strip():
        return "empty"

    # Tamil Unicode
    tamil_chars = re.findall(r"[\u0B80-\u0BFF]", text)

    # English alphabet
    english_chars = re.findall(r"[A-Za-z]", text)

    tanglish_count = count_tanglish_words(text)

    # Tamil script
    if tamil_chars and english_chars:
        return "mixed_script"

    if tamil_chars:
        return "tamil_script"

    # Romanized Tamil
    if tanglish_count >= 1:
        return "tanglish"

    if english_chars:
        return "english"

    return "other"


# -----------------------------------
# Analyze each person
# -----------------------------------

results = {}

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
    tanglish_words = Counter()

    total_tanglish_words = 0

    for message in sender_messages:

        text = message.get("message", "")

        language = detect_language(text)

        language_counts[language] += 1

        words = get_words(text)

        for word in words:

            if word in TANGLISH_WORDS:
                tanglish_words[word] += 1
                total_tanglish_words += 1

    results[sender] = {
        "total_messages": len(sender_messages),
        "language_distribution": dict(language_counts),
        "total_tanglish_words": total_tanglish_words,
        "top_tanglish_words": dict(
            tanglish_words.most_common(30)
        )
    }


# -----------------------------------
# Print results
# -----------------------------------

print("\n========== TANGLISH ANALYSIS ==========\n")

for sender, data in results.items():

    print(sender)

    print(f"  Messages: {data['total_messages']}")

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

    print(
        f"  Total Tanglish words: "
        f"{data['total_tanglish_words']}"
    )

    print("  Top Tanglish words:")

    for word, count in data["top_tanglish_words"].items():
        print(f"    {word}: {count}")

    print()


# -----------------------------------
# Save results
# -----------------------------------

OUTPUT_FILE = Path(
    "data/processed/tanglish_analysis.json"
)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        results,
        file,
        ensure_ascii=False,
        indent=2
    )

print(f"Saved to: {OUTPUT_FILE}")