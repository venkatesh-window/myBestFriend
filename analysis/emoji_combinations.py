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
    "data/processed/emoji_combinations.json"
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
# COMPOUND EMOJI EXTRACTION
# ============================================================

def extract_emoji_sequences(text):

    sequences = []
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
                    sequences.append(
                        text[i:j + 1]
                    )

                    i = j + 1
                    continue

        # ----------------------------------------------------
        # Flags
        # ----------------------------------------------------

        if is_regional_indicator(char):

            if (
                i + 1 < len(text)
                and is_regional_indicator(text[i + 1])
            ):
                sequences.append(
                    text[i:i + 2]
                )

                i += 2
                continue

        # ----------------------------------------------------
        # Emoji
        # ----------------------------------------------------

        if is_emoji_base(char):

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

            sequences.append(sequence)
            continue

        i += 1

    return sequences


# ============================================================
# LOAD MESSAGES
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
            "messages_with_multiple_emojis": 0,
            "emoji_pair_counter": Counter(),
            "emoji_triple_counter": Counter(),
            "emoji_sequence_counter": Counter()
        }

    speaker_data[sender][
        "messages_analyzed"
    ] += 1

    emojis = extract_emoji_sequences(message)

    if not emojis:
        continue

    speaker_data[sender][
        "messages_with_emoji"
    ] += 1

    # --------------------------------------------------------
    # Multiple emoji messages
    # --------------------------------------------------------

    if len(emojis) >= 2:

        speaker_data[sender][
            "messages_with_multiple_emojis"
        ] += 1

    # --------------------------------------------------------
    # Full emoji sequence
    # --------------------------------------------------------

    if len(emojis) >= 2:

        sequence = tuple(emojis)

        speaker_data[sender][
            "emoji_sequence_counter"
        ][sequence] += 1

    # --------------------------------------------------------
    # Adjacent pairs
    # --------------------------------------------------------

    for i in range(len(emojis) - 1):

        pair = (
            emojis[i],
            emojis[i + 1]
        )

        speaker_data[sender][
            "emoji_pair_counter"
        ][pair] += 1

    # --------------------------------------------------------
    # Adjacent triples
    # --------------------------------------------------------

    for i in range(len(emojis) - 2):

        triple = (
            emojis[i],
            emojis[i + 1],
            emojis[i + 2]
        )

        speaker_data[sender][
            "emoji_triple_counter"
        ][triple] += 1


# ============================================================
# BUILD OUTPUT
# ============================================================

output = {
    "analysis": "emoji_combinations",
    "description": (
        "Analyzes repeated emoji sequences, adjacent "
        "emoji pairs, triples, and multi-emoji messages."
    ),
    "speakers": {}
}


for speaker, data in speaker_data.items():

    pair_counter = data[
        "emoji_pair_counter"
    ]

    triple_counter = data[
        "emoji_triple_counter"
    ]

    sequence_counter = data[
        "emoji_sequence_counter"
    ]

    total_messages = data[
        "messages_analyzed"
    ]

    multiple_messages = data[
        "messages_with_multiple_emojis"
    ]

    multiple_percentage = (
        multiple_messages
        / total_messages
        * 100
        if total_messages
        else 0
    )

    # --------------------------------------------------------
    # Pairs
    # --------------------------------------------------------

    top_pairs = []

    for pair, count in pair_counter.most_common(30):

        top_pairs.append({
            "combination": "".join(pair),
            "components": list(pair),
            "count": count
        })

    # --------------------------------------------------------
    # Triples
    # --------------------------------------------------------

    top_triples = []

    for triple, count in triple_counter.most_common(30):

        top_triples.append({
            "combination": "".join(triple),
            "components": list(triple),
            "count": count
        })

    # --------------------------------------------------------
    # Full sequences
    # --------------------------------------------------------

    top_sequences = []

    for sequence, count in (
        sequence_counter.most_common(30)
    ):

        top_sequences.append({
            "sequence": "".join(sequence),
            "components": list(sequence),
            "emoji_count": len(sequence),
            "count": count
        })

    # --------------------------------------------------------
    # Save speaker result
    # --------------------------------------------------------

    output["speakers"][speaker] = {

        "messages_analyzed":
            total_messages,

        "messages_with_emoji":
            data["messages_with_emoji"],

        "messages_with_multiple_emojis":
            multiple_messages,

        "multiple_emoji_message_percentage":
            round(
                multiple_percentage,
                2
            ),

        "unique_emoji_pairs":
            len(pair_counter),

        "unique_emoji_triples":
            len(triple_counter),

        "unique_full_emoji_sequences":
            len(sequence_counter),

        "top_30_emoji_pairs":
            top_pairs,

        "top_30_emoji_triples":
            top_triples,

        "top_30_full_emoji_sequences":
            top_sequences
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
    "\n========== EMOJI COMBINATIONS ==========\n"
)


for speaker, data in output["speakers"].items():

    print(f"Speaker: {speaker}")

    print(
        f"Messages with multiple emojis: "
        f"{data['messages_with_multiple_emojis']}"
    )

    print(
        f"Multiple-emoji message %: "
        f"{data['multiple_emoji_message_percentage']}%"
    )

    print(
        f"Unique emoji pairs: "
        f"{data['unique_emoji_pairs']}"
    )

    print(
        f"Unique emoji triples: "
        f"{data['unique_emoji_triples']}"
    )

    print("\nTop emoji pairs:")

    for item in data["top_30_emoji_pairs"][:15]:

        print(
            f"  {item['combination']} "
            f"→ {item['count']}"
        )

    print("\nTop emoji triples:")

    for item in data["top_30_emoji_triples"][:10]:

        print(
            f"  {item['combination']} "
            f"→ {item['count']}"
        )

    print(
        "\n----------------------------------------"
    )


print(
    f"\nSaved to: {OUTPUT_FILE}"
)