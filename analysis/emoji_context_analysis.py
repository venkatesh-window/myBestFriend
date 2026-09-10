import json
import re
from collections import Counter, defaultdict
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "data/processed/messages.json"
)

OUTPUT_FILE = Path(
    "data/processed/emoji_context_analysis.json"
)

WINDOW_SIZE = 3
MIN_EMOJI_COUNT = 2
TOP_WORDS = 20


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
# EXTRACT COMPOUND EMOJIS
# ============================================================

def extract_emojis(text):

    results = []
    i = 0

    while i < len(text):

        char = text[i]

        # ----------------------------------------------------
        # Keycaps
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
        # Flags
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
# WORD TOKENIZATION
# ============================================================

def tokenize_words(text):

    return re.findall(
        r"[a-zA-Z]+(?:'[a-zA-Z]+)?",
        text.lower()
    )


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
# DATA STRUCTURES
# ============================================================

speaker_data = {}


# ============================================================
# ANALYZE
# ============================================================

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
            "emoji_messages": 0,
            "emoji_counter": Counter(),
            "context_words": defaultdict(Counter),
            "emoji_examples": defaultdict(list)
        }

    data = speaker_data[sender]

    data["messages_analyzed"] += 1

    emojis = extract_emojis(message)

    if not emojis:
        continue

    data["emoji_messages"] += 1

    # --------------------------------------------------------
    # Process each emoji
    # --------------------------------------------------------

    for emoji_info in emojis:

        emoji = emoji_info["emoji"]

        data["emoji_counter"][emoji] += 1

        # Text before emoji
        before_text = message[
            :emoji_info["start"]
        ]

        # Text after emoji
        after_text = message[
            emoji_info["end"]:
        ]

        before_words = tokenize_words(
            before_text
        )

        after_words = tokenize_words(
            after_text
        )

        # ----------------------------------------------------
        # Take nearby words
        # ----------------------------------------------------

        nearby_words = (
            before_words[-WINDOW_SIZE:]
            + after_words[:WINDOW_SIZE]
        )

        for word in nearby_words:

            data["context_words"][
                emoji
            ][word] += 1

        # ----------------------------------------------------
        # Store examples
        # ----------------------------------------------------

        if len(
            data["emoji_examples"][emoji]
        ) < 5:

            data["emoji_examples"][
                emoji
            ].append(message)


# ============================================================
# BUILD OUTPUT
# ============================================================

output = {
    "analysis": "emoji_context_analysis",
    "description": (
        "Connects emojis with nearby words and example "
        "messages to identify context-dependent usage."
    ),
    "window_size_words": WINDOW_SIZE,
    "speakers": {}
}


for speaker, data in speaker_data.items():

    speaker_output = {
        "messages_analyzed":
            data["messages_analyzed"],

        "messages_with_emoji":
            data["emoji_messages"],

        "emoji_contexts": {}
    }

    # --------------------------------------------------------
    # Each emoji
    # --------------------------------------------------------

    for emoji, count in (
        data["emoji_counter"].most_common()
    ):

        if count < MIN_EMOJI_COUNT:
            continue

        context_counter = data[
            "context_words"
        ][emoji]

        speaker_output[
            "emoji_contexts"
        ][emoji] = {

            "usage_count":
                count,

            "top_context_words": [
                {
                    "word": word,
                    "count": word_count
                }

                for word, word_count
                in context_counter.most_common(
                    TOP_WORDS
                )
            ],

            "examples":
                data["emoji_examples"][emoji]
        }

    output["speakers"][speaker] = speaker_output


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
    "\n========== EMOJI CONTEXT ANALYSIS ==========\n"
)

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

    print("\nEmoji contexts:")

    for emoji, context in list(
        data["emoji_contexts"].items()
    )[:15]:

        print(
            f"\n  {emoji} "
            f"({context['usage_count']} uses)"
        )

        words = context[
            "top_context_words"
        ]

        if words:

            print("    Context words:")

            print(
                "    "
                + ", ".join(
                    f"{x['word']}({x['count']})"
                    for x in words[:10]
                )
            )

        if context["examples"]:

            print("    Example:")

            print(
                "    "
                + context["examples"][0][:120]
            )

    print(
        "\n--------------------------------------------"
    )


print(
    f"\nSaved to: {OUTPUT_FILE}"
)