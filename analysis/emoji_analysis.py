import json
from pathlib import Path
from collections import Counter, defaultdict


# ==========================================
# 1. LOAD DATA
# ==========================================

INPUT_FILE = Path("data/processed/messages.json")

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# ==========================================
# 2. EMOJI DETECTION
# ==========================================

def extract_emojis(text):
    emojis = []

    for character in text:

        # Unicode ranges commonly containing emojis
        code = ord(character)

        if (
            0x1F300 <= code <= 0x1FAFF
            or 0x2600 <= code <= 0x26FF
            or 0x2700 <= code <= 0x27BF
        ):
            emojis.append(character)

    return emojis


# ==========================================
# 3. STORAGE
# ==========================================

emoji_counts = defaultdict(Counter)
emoji_message_counts = defaultdict(int)
message_counts = Counter()


# ==========================================
# 4. ANALYZE
# ==========================================

for message in messages:

    sender = message.get("sender")

    if not sender:
        continue

    text = message.get("message") or ""

    message_counts[sender] += 1

    emojis = extract_emojis(text)

    if emojis:

        emoji_message_counts[sender] += 1

        for emoji in emojis:
            emoji_counts[sender][emoji] += 1


# ==========================================
# 5. REPORT
# ==========================================

print("=" * 65)
print("                    EMOJI ANALYSIS")
print("=" * 65)


for sender in message_counts:

    total_messages = message_counts[sender]
    messages_with_emoji = emoji_message_counts[sender]

    percentage = (
        messages_with_emoji / total_messages * 100
        if total_messages
        else 0
    )

    total_emojis = sum(
        emoji_counts[sender].values()
    )

    unique_emojis = len(
        emoji_counts[sender]
    )


    print()
    print("=" * 65)
    print(f"SENDER: {sender}")
    print("=" * 65)

    print()
    print("SUMMARY")
    print("-" * 30)

    print(f"Total messages       : {total_messages}")
    print(f"Messages with emoji  : {messages_with_emoji}")
    print(f"Emoji percentage     : {percentage:.2f}%")
    print(f"Total emojis         : {total_emojis}")
    print(f"Unique emojis        : {unique_emojis}")


    print()
    print("MOST USED EMOJIS")
    print("-" * 30)

    for emoji, count in emoji_counts[sender].most_common(20):

        print(f"{emoji} : {count}")


print()
print("=" * 65)
print("✅ EMOJI ANALYSIS COMPLETED")
print("=" * 65)
# -----------------------------------
# Save analysis results
# -----------------------------------

OUTPUT_FILE = Path("data/processed/emoji_analysis.json")

emoji_results = {}

for sender in message_counts:

    total_messages = message_counts[sender]
    messages_with_emoji = emoji_message_counts[sender]

    percentage = (
        messages_with_emoji / total_messages * 100
        if total_messages
        else 0
    )

    total_emojis = sum(
        emoji_counts[sender].values()
    )

    unique_emojis = len(
        emoji_counts[sender]
    )

    emoji_results[sender] = {
        "total_messages": total_messages,
        "messages_with_emoji": messages_with_emoji,
        "emoji_percentage": round(percentage, 2),
        "total_emojis": total_emojis,
        "unique_emojis": unique_emojis,
        "top_emojis": dict(
            emoji_counts[sender].most_common(20)
        )
    }


with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        emoji_results,
        file,
        ensure_ascii=False,
        indent=2
    )

print(f"\nSaved to: {OUTPUT_FILE}")