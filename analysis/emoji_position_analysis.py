import json
from collections import Counter
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "data/processed/messages.json"
)

OUTPUT_FILE = Path(
    "data/processed/emoji_position_analysis.json"
)


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


def is_regional_indicator(char):
    return 0x1F1E6 <= ord(char) <= 0x1F1FF


# ============================================================
# EXTRACT COMPOUND EMOJIS WITH POSITIONS
# ============================================================

def extract_emoji_positions(text):

    results = []
    i = 0

    while i < len(text):

        char = text[i]

        # ----------------------------------------------------
        # Keycap
        # ----------------------------------------------------

        if char.isdigit() or char in "#*":

            if i + 1 < len(text):

                j = i + 1

                if text[j] == "\uFE0F":
                    j += 1

                if (
                    j < len(text)
                    and text[j] == "\u20E3"
                ):

                    results.append({
                        "emoji": text[i:j + 1],
                        "start": i,
                        "end": j + 1
                    })

                    i = j + 1
                    continue

        # ----------------------------------------------------
        # Flag
        # ----------------------------------------------------

        if is_regional_indicator(char):

            if (
                i + 1 < len(text)
                and is_regional_indicator(text[i + 1])
            ):

                results.append({
                    "emoji": text[i:i + 2],
                    "start": i,
                    "end": i + 2
                })

                i += 2
                continue

        # ----------------------------------------------------
        # Normal / compound emoji
        # ----------------------------------------------------

        if is_emoji_base(char):

            start = i
            sequence = char

            i += 1

            # Skin tone
            if (
                i < len(text)
                and is_skin_tone(text[i])
            ):
                sequence += text[i]
                i += 1

            # Variation selector
            if (
                i < len(text)
                and is_variation_selector(text[i])
            ):
                sequence += text[i]
                i += 1

            # ZWJ sequence
            while (
                i < len(text)
                and is_zwj(text[i])
            ):

                sequence += text[i]
                i += 1

                if i >= len(text):
                    break

                if is_emoji_base(text[i]):
                    sequence += text[i]
                    i += 1

                if (
                    i < len(text)
                    and is_skin_tone(text[i])
                ):
                    sequence += text[i]
                    i += 1

                if (
                    i < len(text)
                    and is_variation_selector(text[i])
                ):
                    sequence += text[i]
                    i += 1

            results.append({
                "emoji": sequence,
                "start": start,
                "end": i
            })

            continue

        i += 1

    return results


# ============================================================
# POSITION CLASSIFICATION
# ============================================================

def classify_position(text, emoji):

    start = emoji["start"]
    end = emoji["end"]

    before = text[:start].strip()
    after = text[end:].strip()

    # Emoji is the entire message
    if not before and not after:
        return "only_emoji"

    # Emoji at beginning
    if not before:
        return "beginning"

    # Emoji at end
    if not after:
        return "end"

    # Emoji surrounded by text
    return "middle"


# ============================================================
# LOAD DATA
# ============================================================

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

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
            "emoji_position_counter": Counter(),
            "emoji_counter": Counter(),
            "examples": {
                "beginning": [],
                "middle": [],
                "end": [],
                "only_emoji": []
            }
        }

    speaker_data[sender][
        "messages_analyzed"
    ] += 1

    emojis = extract_emoji_positions(message)

    if not emojis:
        continue

    speaker_data[sender][
        "messages_with_emoji"
    ] += 1

    for emoji in emojis:

        position = classify_position(
            message,
            emoji
        )

        speaker_data[sender][
            "emoji_position_counter"
        ][position] += 1

        speaker_data[sender][
            "emoji_counter"
        ][emoji["emoji"]] += 1

        # Keep a few examples
        if (
            len(
                speaker_data[sender][
                    "examples"
                ][position]
            ) < 5
        ):

            speaker_data[sender][
                "examples"
            ][position].append({
                "emoji": emoji["emoji"],
                "message": message
            })


# ============================================================
# BUILD OUTPUT
# ============================================================

output = {
    "analysis": "emoji_position_analysis",
    "description": (
        "Analyzes where emojis appear within messages."
    ),
    "speakers": {}
}


for speaker, data in speaker_data.items():

    counter = data[
        "emoji_position_counter"
    ]

    total_emojis = sum(counter.values())

    position_profile = {}

    for position in [
        "beginning",
        "middle",
        "end",
        "only_emoji"
    ]:

        count = counter[position]

        percentage = (
            count / total_emojis * 100
            if total_emojis
            else 0
        )

        position_profile[position] = {
            "count": count,
            "percentage": round(
                percentage,
                2
            )
        }

    # --------------------------------------------------------
    # Message-level classification
    # --------------------------------------------------------

    message_position_counts = Counter()

    for position in [
        "beginning",
        "middle",
        "end",
        "only_emoji"
    ]:

        message_position_counts[position] = len(
            data["examples"][position]
        )

    output["speakers"][speaker] = {

        "messages_analyzed":
            data["messages_analyzed"],

        "messages_with_emoji":
            data["messages_with_emoji"],

        "total_emojis":
            total_emojis,

        "position_profile":
            position_profile,

        "examples":
            data["examples"]
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

print(
    "\n========== EMOJI POSITION ANALYSIS ==========\n"
)

for speaker, data in output["speakers"].items():

    print(f"Speaker: {speaker}")

    print(
        f"Messages with emoji: "
        f"{data['messages_with_emoji']}"
    )

    print(
        f"Total emojis: "
        f"{data['total_emojis']}"
    )

    print("\nPosition profile:")

    for position, stats in (
        data["position_profile"].items()
    ):

        print(
            f"  {position:>10}: "
            f"{stats['count']} "
            f"({stats['percentage']}%)"
        )

    print("\nExamples:")

    for position, examples in (
        data["examples"].items()
    ):

        if not examples:
            continue

        print(f"\n  {position}:")

        for example in examples:

            print(
                f"    {example['emoji']} "
                f"→ {example['message'][:100]}"
            )

    print(
        "\n--------------------------------------------"
    )


print(
    f"\nSaved to: {OUTPUT_FILE}"
)