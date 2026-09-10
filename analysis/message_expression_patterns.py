import json
from pathlib import Path
from collections import Counter


BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "message_expression_patterns.json"


# ---------------------------------------------------------
# LOAD MESSAGES
# ---------------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# ---------------------------------------------------------
# ANALYZE
# ---------------------------------------------------------

speaker_data = {}


for i, message in enumerate(messages):

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
            "single_message_expressions": 0,
            "possible_continuation_messages": 0,
            "message_lengths": [],
        }

    data = speaker_data[sender]

    data["messages_analyzed"] += 1

    # Number of words in this message
    word_count = len(text.split())

    data["message_lengths"].append(word_count)


    # -----------------------------------------------------
    # CHECK WHETHER NEXT MESSAGE IS SAME SPEAKER
    # -----------------------------------------------------

    next_same_speaker = False

    for j in range(i + 1, len(messages)):

        next_message = messages[j]

        next_sender = next_message.get("sender")

        if not next_sender:
            continue

        if next_message.get("is_deleted"):
            continue

        if next_message.get("is_media"):
            continue

        if not next_message.get("message"):
            continue

        if next_sender == sender:
            next_same_speaker = True

        break


    if next_same_speaker:

        data["possible_continuation_messages"] += 1

    else:

        data["single_message_expressions"] += 1


# ---------------------------------------------------------
# BUILD PROFILE
# ---------------------------------------------------------

profile = {}


for speaker, data in speaker_data.items():

    total = data["messages_analyzed"]

    if total > 0:

        continuation_percentage = (
            data["possible_continuation_messages"]
            / total
        ) * 100

        single_message_percentage = (
            data["single_message_expressions"]
            / total
        ) * 100

    else:

        continuation_percentage = 0
        single_message_percentage = 0


    # Message length categories
    very_short = sum(
        1
        for length in data["message_lengths"]
        if length <= 3
    )

    short = sum(
        1
        for length in data["message_lengths"]
        if 4 <= length <= 10
    )

    medium = sum(
        1
        for length in data["message_lengths"]
        if 11 <= length <= 30
    )

    long = sum(
        1
        for length in data["message_lengths"]
        if length > 30
    )


    profile[speaker] = {

        "messages_analyzed": total,

        "single_message_expressions":
            data["single_message_expressions"],

        "single_message_percentage":
            round(
                single_message_percentage,
                2
            ),

        "possible_continuation_messages":
            data["possible_continuation_messages"],

        "possible_continuation_percentage":
            round(
                continuation_percentage,
                2
            ),

        "message_length_categories": {

            "very_short_1_to_3_words":
                very_short,

            "short_4_to_10_words":
                short,

            "medium_11_to_30_words":
                medium,

            "long_31_plus_words":
                long,
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

print(
    "\n========== MESSAGE EXPRESSION PATTERNS ==========\n"
)


for speaker, data in profile.items():

    print(f"Speaker: {speaker}")

    print(
        f"  Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print(
        f"  Single-message expressions: "
        f"{data['single_message_expressions']}"
    )

    print(
        f"  Single-message percentage: "
        f"{data['single_message_percentage']}%"
    )

    print(
        f"  Possible continuation messages: "
        f"{data['possible_continuation_messages']}"
    )

    print(
        f"  Continuation percentage: "
        f"{data['possible_continuation_percentage']}%"
    )

    print("\n  Message length categories:")

    for category, count in data[
        "message_length_categories"
    ].items():

        print(
            f"    {category}: {count}"
        )

    print()


print("Saved to:")
print(OUTPUT_FILE)