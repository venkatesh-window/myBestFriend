import json
import re
from pathlib import Path
from collections import Counter


BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "emoji_extraction.json"


# ---------------------------------------------------------
# LOAD MESSAGES
# ---------------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# ---------------------------------------------------------
# EMOJI DETECTION
# ---------------------------------------------------------

# Common Unicode ranges containing emojis/symbols.
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F5FF"  # Miscellaneous Symbols & Pictographs
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F680-\U0001F6FF"  # Transport & Map
    "\U0001F700-\U0001F77F"  # Alchemical Symbols
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols
    "\U0001FA00-\U0001FAFF"  # Extended Symbols
    "\U00002700-\U000027BF"  # Dingbats
    "\U00002600-\U000026FF"  # Miscellaneous Symbols
    "]"
)


def extract_emojis(text):
    """
    Extract individual emoji code points/symbols.

    This is the first-stage extractor.
    Compound emoji sequences will be handled separately.
    """

    return EMOJI_PATTERN.findall(text)


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

    # Create speaker profile
    if sender not in speaker_data:

        speaker_data[sender] = {
            "messages_analyzed": 0,
            "messages_with_emoji": 0,
            "total_emojis": 0,
            "emoji_counter": Counter(),
        }

    data = speaker_data[sender]

    data["messages_analyzed"] += 1

    # Extract emojis
    emojis = extract_emojis(text)

    if emojis:

        data["messages_with_emoji"] += 1

        data["total_emojis"] += len(emojis)

        data["emoji_counter"].update(emojis)


# ---------------------------------------------------------
# BUILD PROFILE
# ---------------------------------------------------------

profile = {}


for speaker, data in speaker_data.items():

    total_messages = data["messages_analyzed"]

    total_emojis = data["total_emojis"]

    if total_messages > 0:

        emoji_message_percentage = (
            data["messages_with_emoji"]
            / total_messages
        ) * 100

        emoji_per_message = (
            total_emojis
            / total_messages
        )

    else:

        emoji_message_percentage = 0
        emoji_per_message = 0


    # Top emojis
    top_emojis = []

    for emoji, count in data[
        "emoji_counter"
    ].most_common(30):

        top_emojis.append({
            "emoji": emoji,
            "count": count
        })


    profile[speaker] = {

        "messages_analyzed":
            total_messages,

        "messages_with_emoji":
            data["messages_with_emoji"],

        "emoji_message_percentage":
            round(
                emoji_message_percentage,
                2
            ),

        "total_emojis":
            total_emojis,

        "emoji_per_message":
            round(
                emoji_per_message,
                3
            ),

        "unique_emojis":
            len(data["emoji_counter"]),

        "top_emojis":
            top_emojis,
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

print("\n========== EMOJI EXTRACTION ==========\n")


for speaker, data in profile.items():

    print(f"Speaker: {speaker}")

    print(
        f"  Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print(
        f"  Messages with emoji: "
        f"{data['messages_with_emoji']}"
    )

    print(
        f"  Emoji message percentage: "
        f"{data['emoji_message_percentage']}%"
    )

    print(
        f"  Total emojis: "
        f"{data['total_emojis']}"
    )

    print(
        f"  Emojis/message: "
        f"{data['emoji_per_message']}"
    )

    print(
        f"  Unique emojis: "
        f"{data['unique_emojis']}"
    )

    print("\n  Top emojis:")

    for item in data["top_emojis"][:20]:

        print(
            f"    {item['emoji']} → "
            f"{item['count']}"
        )

    print()


print("Saved to:")
print(OUTPUT_FILE)