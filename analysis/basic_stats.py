import json
from pathlib import Path
from collections import Counter


# ==========================================
# 1. LOAD DATA
# ==========================================

INPUT_FILE = Path("data/processed/messages.json")

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


print("✅ messages.json loaded")
print(f"Total messages: {len(messages)}")


# ==========================================
# 2. BASIC COUNTS
# ==========================================

sender_counts = Counter()

total_characters = 0
total_words = 0

media_count = 0
deleted_count = 0
empty_count = 0
multiline_count = 0


# ==========================================
# 3. ANALYZE EACH MESSAGE
# ==========================================

for message in messages:

    sender = message.get("sender")
    text = message.get("message") or ""


    # --------------------------
    # Sender
    # --------------------------

    if sender:
        sender_counts[sender] += 1


    # --------------------------
    # Characters
    # --------------------------

    total_characters += len(text)


    # --------------------------
    # Words
    # --------------------------

    total_words += len(text.split())


    # --------------------------
    # Media
    # --------------------------

    if message.get("is_media"):
        media_count += 1


    # --------------------------
    # Deleted
    # --------------------------

    if message.get("is_deleted"):
        deleted_count += 1


    # --------------------------
    # Empty
    # --------------------------

    if text.strip() == "":
        empty_count += 1


    # --------------------------
    # Multiline
    # --------------------------

    if "\n" in text:
        multiline_count += 1


# ==========================================
# 4. AVERAGES
# ==========================================

total_messages = len(messages)

average_characters = (
    total_characters / total_messages
    if total_messages
    else 0
)

average_words = (
    total_words / total_messages
    if total_messages
    else 0
)


# ==========================================
# 5. REPORT
# ==========================================

print()
print("=" * 55)
print("              BASIC CHAT ANALYSIS")
print("=" * 55)

print()

print("GENERAL")
print("-" * 30)

print(f"Total messages       : {total_messages}")
print(f"Total characters     : {total_characters}")
print(f"Total words         : {total_words}")

print(f"Average characters   : {average_characters:.2f}")
print(f"Average words        : {average_words:.2f}")


print()
print("MESSAGES PER PERSON")
print("-" * 30)

for sender, count in sender_counts.most_common():

    percentage = (count / total_messages) * 100

    print(
        f"{sender}: "
        f"{count} messages "
        f"({percentage:.2f}%)"
    )


print()
print("MESSAGE TYPES")
print("-" * 30)

print(f"Media messages       : {media_count}")
print(f"Deleted messages     : {deleted_count}")
print(f"Empty messages       : {empty_count}")
print(f"Multiline messages   : {multiline_count}")


print()
print("=" * 55)
print("✅ BASIC ANALYSIS COMPLETED")
print("=" * 55)
# -----------------------------------
# Save analysis results
# -----------------------------------

stats = {
    "general": {
        "total_messages": total_messages,
        "total_characters": total_characters,
        "total_words": total_words,
        "average_characters": round(average_characters, 2),
        "average_words": round(average_words, 2)
    },

    "messages_per_person": dict(sender_counts),

    "message_types": {
        "media_messages": media_count,
        "deleted_messages": deleted_count,
        "empty_messages": empty_count,
        "multiline_messages": multiline_count
    }
}


OUTPUT_FILE = Path("data/processed/basic_stats.json")

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(
        stats,
        file,
        ensure_ascii=False,
        indent=2
    )

print(f"\nSaved to: {OUTPUT_FILE}")