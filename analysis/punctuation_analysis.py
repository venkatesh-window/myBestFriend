import json
import re
from pathlib import Path
from collections import Counter


BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "punctuation_analysis.json"


# ---------------------------------------------------------
# LOAD MESSAGES
# ---------------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# ---------------------------------------------------------
# PUNCTUATION WE WANT TO ANALYZE
# ---------------------------------------------------------

PUNCTUATION_MARKS = {
    ".": "period",
    ",": "comma",
    "?": "question_mark",
    "!": "exclamation_mark",
    ":": "colon",
    ";": "semicolon",
    "'": "apostrophe",
    '"': "quotation_mark",
    "-": "hyphen",
}


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

    if sender not in speaker_data:

        speaker_data[sender] = {
            "messages_analyzed": 0,
            "punctuation_counts": Counter(),
            "repeated_patterns": Counter(),
            "messages_with_punctuation": 0,
        }

    data = speaker_data[sender]

    data["messages_analyzed"] += 1


    # -----------------------------------------------------
    # COUNT INDIVIDUAL PUNCTUATION
    # -----------------------------------------------------

    has_punctuation = False

    for mark, name in PUNCTUATION_MARKS.items():

        count = text.count(mark)

        if count > 0:
            has_punctuation = True

        data["punctuation_counts"][name] += count


    if has_punctuation:

        data["messages_with_punctuation"] += 1


    # -----------------------------------------------------
    # REPEATED PUNCTUATION
    # -----------------------------------------------------

    repeated = re.findall(
        r"[!?.,:;]{2,}",
        text
    )

    for pattern in repeated:

        data["repeated_patterns"][pattern] += 1


# ---------------------------------------------------------
# BUILD PROFILE
# ---------------------------------------------------------

profile = {}


for speaker, data in speaker_data.items():

    total_messages = data["messages_analyzed"]

    punctuation_counts = data["punctuation_counts"]

    total_punctuation = sum(
        punctuation_counts.values()
    )

    if total_messages > 0:

        punctuation_per_message = (
            total_punctuation
            / total_messages
        )

        punctuation_message_percentage = (
            data["messages_with_punctuation"]
            / total_messages
        ) * 100

    else:

        punctuation_per_message = 0
        punctuation_message_percentage = 0


    # Convert Counter to normal dictionary
    punctuation_profile = {}

    for name, count in punctuation_counts.items():

        punctuation_profile[name] = {
            "count": count,
            "per_message": round(
                count / total_messages,
                3
            ) if total_messages else 0,
        }


    # Sort repeated patterns by frequency
    repeated_patterns = sorted(
        data["repeated_patterns"].items(),
        key=lambda item: item[1],
        reverse=True
    )


    profile[speaker] = {

        "messages_analyzed":
            total_messages,

        "messages_with_punctuation":
            data["messages_with_punctuation"],

        "punctuation_message_percentage":
            round(
                punctuation_message_percentage,
                2
            ),

        "total_punctuation_marks":
            total_punctuation,

        "punctuation_marks_per_message":
            round(
                punctuation_per_message,
                3
            ),

        "punctuation_profile":
            punctuation_profile,

        "repeated_punctuation_patterns": {
            pattern: count
            for pattern, count
            in repeated_patterns
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

print("\n========== PUNCTUATION ANALYSIS ==========\n")


for speaker, data in profile.items():

    print(f"Speaker: {speaker}")

    print(
        f"  Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print(
        f"  Messages with punctuation: "
        f"{data['messages_with_punctuation']}"
    )

    print(
        f"  Punctuation message percentage: "
        f"{data['punctuation_message_percentage']}%"
    )

    print(
        f"  Total punctuation marks: "
        f"{data['total_punctuation_marks']}"
    )

    print(
        f"  Punctuation marks/message: "
        f"{data['punctuation_marks_per_message']}"
    )

    print("\n  Punctuation profile:")

    for name, values in data[
        "punctuation_profile"
    ].items():

        print(
            f"    {name}: "
            f"{values['count']} "
            f"({values['per_message']}/message)"
        )


    print("\n  Repeated punctuation:")

    if data["repeated_punctuation_patterns"]:

        for pattern, count in list(
            data["repeated_punctuation_patterns"].items()
        )[:20]:

            print(
                f"    {pattern} → {count}"
            )

    else:

        print("    None")


    print("\n")


print("Saved to:")
print(OUTPUT_FILE)