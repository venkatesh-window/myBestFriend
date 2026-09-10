import json
import re
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "data/processed/messages.json"
)

OUTPUT_FILE = Path(
    "data/processed/tamil_script_detection.json"
)


# Tamil Unicode block:
# U+0B80 - U+0BFF
TAMIL_RANGE = (0x0B80, 0x0BFF)


# ============================================================
# CHARACTER HELPERS
# ============================================================

def is_tamil_char(char):
    code = ord(char)

    return (
        TAMIL_RANGE[0]
        <= code
        <= TAMIL_RANGE[1]
    )


def is_english_char(char):
    return (
        ("a" <= char.lower() <= "z")
    )


def count_characters(text):

    tamil = 0
    english = 0
    other_letters = 0

    for char in text:

        if is_tamil_char(char):

            tamil += 1

        elif is_english_char(char):

            english += 1

        elif char.isalpha():

            other_letters += 1

    return tamil, english, other_letters


# ============================================================
# CLASSIFY MESSAGE
# ============================================================

def classify_message(text):

    tamil_count, english_count, other_count = (
        count_characters(text)
    )

    total_language_chars = (
        tamil_count
        + english_count
        + other_count
    )

    if total_language_chars == 0:

        return {
            "language": "unknown",
            "tamil_chars": 0,
            "english_chars": 0,
            "other_letter_chars": 0
        }

    tamil_percentage = (
        tamil_count
        / total_language_chars
        * 100
    )

    english_percentage = (
        english_count
        / total_language_chars
        * 100
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    if tamil_count > 0 and english_count > 0:

        language = "mixed"

    elif tamil_count > 0:

        language = "tamil_script"

    elif english_count > 0:

        language = "english"

    else:

        language = "other"

    return {
        "language": language,
        "tamil_chars": tamil_count,
        "english_chars": english_count,
        "other_letter_chars": other_count,
        "tamil_percentage": round(
            tamil_percentage,
            2
        ),
        "english_percentage": round(
            english_percentage,
            2
        )
    }


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
            "language_counts": {
                "tamil_script": 0,
                "english": 0,
                "mixed": 0,
                "other": 0,
                "unknown": 0
            },
            "tamil_chars": 0,
            "english_chars": 0,
            "examples": {
                "tamil_script": [],
                "english": [],
                "mixed": []
            }
        }

    data = speaker_data[sender]

    data["messages_analyzed"] += 1

    result = classify_message(message)

    language = result["language"]

    data["language_counts"][language] += 1

    data["tamil_chars"] += result[
        "tamil_chars"
    ]

    data["english_chars"] += result[
        "english_chars"
    ]

    # --------------------------------------------------------
    # Store examples
    # --------------------------------------------------------

    if language in data["examples"]:

        if len(
            data["examples"][language]
        ) < 10:

            data["examples"][language].append(
                message
            )


# ============================================================
# BUILD OUTPUT
# ============================================================

output = {
    "analysis": "tamil_script_detection",
    "description": (
        "Detects Tamil Unicode characters and classifies "
        "messages as Tamil script, English, mixed, other, "
        "or unknown."
    ),
    "speakers": {}
}


for speaker, data in speaker_data.items():

    total = data["messages_analyzed"]

    language_profile = {}

    for language, count in (
        data["language_counts"].items()
    ):

        percentage = (
            count / total * 100
            if total
            else 0
        )

        language_profile[language] = {
            "messages": count,
            "percentage": round(
                percentage,
                2
            )
        }

    output["speakers"][speaker] = {

        "messages_analyzed": total,

        "language_profile":
            language_profile,

        "total_tamil_characters":
            data["tamil_chars"],

        "total_english_characters":
            data["english_chars"],

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
    "\n========== TAMIL SCRIPT DETECTION ==========\n"
)

for speaker, data in output[
    "speakers"
].items():

    print(f"Speaker: {speaker}")

    print(
        f"Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print("\nLanguage profile:")

    for language, stats in (
        data["language_profile"].items()
    ):

        print(
            f"  {language:>12}: "
            f"{stats['messages']} "
            f"({stats['percentage']}%)"
        )

    print(
        f"\nTamil characters: "
        f"{data['total_tamil_characters']}"
    )

    print(
        f"English characters: "
        f"{data['total_english_characters']}"
    )

    print("\nExamples:")

    for language, examples in (
        data["examples"].items()
    ):

        if not examples:
            continue

        print(f"\n  {language}:")

        for example in examples[:3]:

            print(
                f"    {example[:120]}"
            )

    print(
        "\n--------------------------------------------"
    )


print(
    f"\nSaved to: {OUTPUT_FILE}"
)