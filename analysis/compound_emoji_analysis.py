import json
import re
from collections import Counter
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path("data/processed/messages.json")
OUTPUT_FILE = Path("data/processed/compound_emoji_analysis.json")


# ============================================================
# EMOJI DETECTION
# ============================================================

def is_emoji_base(char):
    code = ord(char)

    return (
        0x1F300 <= code <= 0x1FAFF
        or 0x2600 <= code <= 0x27BF
        or 0x2300 <= code <= 0x23FF
        or 0x2B00 <= code <= 0x2BFF
    )


def is_skin_tone(char):
    return 0x1F3FB <= ord(char) <= 0x1F3FF


def is_variation_selector(char):
    return char == "\uFE0F"


def is_zwj(char):
    return char == "\u200D"


def is_combining_keycap(char):
    return char == "\u20E3"


def is_regional_indicator(char):
    return 0x1F1E6 <= ord(char) <= 0x1F1FF


# ============================================================
# COMPOUND EMOJI EXTRACTION
# ============================================================

def extract_emoji_sequences(text):
    sequences = []
    i = 0

    while i < len(text):

        char = text[i]

        # ----------------------------------------------------
        # Keycap emoji
        # Examples: 1️⃣ 2️⃣ #️⃣ *️⃣
        # ----------------------------------------------------

        if (
            char.isdigit()
            or char in "#*"
        ):
            if i + 1 < len(text):

                j = i + 1

                if j < len(text) and text[j] == "\uFE0F":
                    j += 1

                if j < len(text) and text[j] == "\u20E3":
                    sequences.append(text[i:j + 1])
                    i = j + 1
                    continue

        # ----------------------------------------------------
        # Regional indicator flags
        # Example: 🇮🇳
        # ----------------------------------------------------

        if is_regional_indicator(char):

            if (
                i + 1 < len(text)
                and is_regional_indicator(text[i + 1])
            ):
                sequences.append(text[i:i + 2])
                i += 2
                continue

        # ----------------------------------------------------
        # Normal / compound emoji
        # ----------------------------------------------------

        if is_emoji_base(char):

            sequence = char
            i += 1

            # Skin tone modifier
            if i < len(text) and is_skin_tone(text[i]):
                sequence += text[i]
                i += 1

            # Variation selector
            if i < len(text) and is_variation_selector(text[i]):
                sequence += text[i]
                i += 1

            # ZWJ-connected emoji
            while i < len(text) and is_zwj(text[i]):

                sequence += text[i]
                i += 1

                if i >= len(text):
                    break

                # Next emoji base
                if is_emoji_base(text[i]):
                    sequence += text[i]
                    i += 1

                # Optional skin tone
                if i < len(text) and is_skin_tone(text[i]):
                    sequence += text[i]
                    i += 1

                # Optional variation selector
                if i < len(text) and is_variation_selector(text[i]):
                    sequence += text[i]
                    i += 1

            # Optional combining keycap
            if i < len(text) and is_combining_keycap(text[i]):
                sequence += text[i]
                i += 1

            sequences.append(sequence)
            continue

        i += 1

    return sequences


# ============================================================
# LOAD DATA
# ============================================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    messages = json.load(f)


# ============================================================
# ANALYSIS
# ============================================================

speaker_data = {}

for item in messages:

    sender = item.get("sender")
    message = item.get("message")

    if not sender:
        continue

    if not message:
        continue

    if item.get("is_media"):
        continue

    if item.get("is_deleted"):
        continue

    if sender not in speaker_data:
        speaker_data[sender] = {
            "messages_analyzed": 0,
            "messages_with_emoji": 0,
            "total_emoji_sequences": 0,
            "emoji_counter": Counter(),
        }

    speaker_data[sender]["messages_analyzed"] += 1

    emojis = extract_emoji_sequences(message)

    if emojis:
        speaker_data[sender]["messages_with_emoji"] += 1
        speaker_data[sender]["total_emoji_sequences"] += len(emojis)
        speaker_data[sender]["emoji_counter"].update(emojis)


# ============================================================
# BUILD OUTPUT
# ============================================================

output = {
    "analysis": "compound_emoji_analysis",
    "description": (
        "Groups emoji code points into practical compound "
        "emoji sequences including skin tones, ZWJ sequences, "
        "regional indicator flags, variation selectors, and keycaps."
    ),
    "speakers": {}
}


for speaker, data in speaker_data.items():

    messages_analyzed = data["messages_analyzed"]
    messages_with_emoji = data["messages_with_emoji"]
    total_emojis = data["total_emoji_sequences"]
    counter = data["emoji_counter"]

    emoji_message_percentage = (
        messages_with_emoji / messages_analyzed * 100
        if messages_analyzed
        else 0
    )

    emojis_per_message = (
        total_emojis / messages_analyzed
        if messages_analyzed
        else 0
    )

    emojis_per_emoji_message = (
        total_emojis / messages_with_emoji
        if messages_with_emoji
        else 0
    )

    output["speakers"][speaker] = {
        "messages_analyzed": messages_analyzed,
        "messages_with_emoji": messages_with_emoji,
        "emoji_message_percentage": round(
            emoji_message_percentage, 2
        ),
        "total_emoji_sequences": total_emojis,
        "unique_emoji_sequences": len(counter),
        "emojis_per_message": round(
            emojis_per_message, 3
        ),
        "emojis_per_emoji_message": round(
            emojis_per_emoji_message, 3
        ),
        "top_30_emoji_sequences": [
            {
                "emoji": emoji,
                "count": count
            }
            for emoji, count in counter.most_common(30)
        ]
    }


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output,
        f,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# DISPLAY
# ============================================================

print("\n========== COMPOUND EMOJI ANALYSIS ==========\n")

for speaker, data in output["speakers"].items():

    print(f"Speaker: {speaker}")

    print(
        f"Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print(
        f"Messages with emoji: "
        f"{data['messages_with_emoji']}"
    )

    print(
        f"Emoji message %: "
        f"{data['emoji_message_percentage']}%"
    )

    print(
        f"Total emoji sequences: "
        f"{data['total_emoji_sequences']}"
    )

    print(
        f"Unique emoji sequences: "
        f"{data['unique_emoji_sequences']}"
    )

    print(
        f"Emojis/message: "
        f"{data['emojis_per_message']}"
    )

    print("\nTop emojis:")

    for item in data["top_30_emoji_sequences"][:15]:
        print(
            f"  {item['emoji']} : "
            f"{item['count']}"
        )

    print("\n--------------------------------------------")


print(
    f"\nSaved to: {OUTPUT_FILE}"
)