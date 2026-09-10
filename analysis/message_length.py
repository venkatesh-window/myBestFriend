import json
from pathlib import Path
from collections import defaultdict


# ==========================================
# 1. LOAD DATA
# ==========================================

INPUT_FILE = Path("data/processed/messages.json")

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# ==========================================
# 2. STORAGE
# ==========================================

stats = defaultdict(lambda: {
    "messages": 0,
    "characters": 0,
    "words": 0,
    "short": 0,
    "medium": 0,
    "long": 0,
    "longest_message": "",
    "longest_length": 0
})


# ==========================================
# 3. ANALYZE
# ==========================================

for message in messages:

    sender = message.get("sender")

    if not sender:
        continue

    text = message.get("message") or ""

    characters = len(text)
    words = len(text.split())


    stats[sender]["messages"] += 1
    stats[sender]["characters"] += characters
    stats[sender]["words"] += words


    # ======================================
    # MESSAGE LENGTH CATEGORY
    # ======================================

    if characters <= 20:

        stats[sender]["short"] += 1

    elif characters <= 100:

        stats[sender]["medium"] += 1

    else:

        stats[sender]["long"] += 1


    # ======================================
    # LONGEST MESSAGE
    # ======================================

    if characters > stats[sender]["longest_length"]:

        stats[sender]["longest_length"] = characters
        stats[sender]["longest_message"] = text


# ==========================================
# 4. REPORT
# ==========================================

print("=" * 65)
print("                 MESSAGE LENGTH ANALYSIS")
print("=" * 65)


for sender, data in stats.items():

    message_count = data["messages"]

    average_characters = (
        data["characters"] / message_count
    )

    average_words = (
        data["words"] / message_count
    )


    print()
    print("=" * 65)
    print(f"SENDER: {sender}")
    print("=" * 65)

    print()
    print("TOTAL")
    print("-" * 30)

    print(f"Messages            : {message_count}")
    print(f"Characters          : {data['characters']}")
    print(f"Words               : {data['words']}")


    print()
    print("AVERAGE")
    print("-" * 30)

    print(
        f"Characters/message  : "
        f"{average_characters:.2f}"
    )

    print(
        f"Words/message       : "
        f"{average_words:.2f}"
    )


    print()
    print("MESSAGE CATEGORIES")
    print("-" * 30)

    print(f"Short  (≤20 chars)  : {data['short']}")
    print(f"Medium (21–100)     : {data['medium']}")
    print(f"Long   (>100)       : {data['long']}")


    print()
    print("LONGEST MESSAGE")
    print("-" * 30)

    print(
        f"Characters: "
        f"{data['longest_length']}"
    )

    print(data["longest_message"])


print()
print("=" * 65)
print("✅ MESSAGE LENGTH ANALYSIS COMPLETED")
print("=" * 65)
# -----------------------------------
# Save analysis results
# -----------------------------------

OUTPUT_FILE = Path("data/processed/message_length.json")

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(
        dict(stats),
        file,
        ensure_ascii=False,
        indent=2
    )

print(f"\nSaved to: {OUTPUT_FILE}")