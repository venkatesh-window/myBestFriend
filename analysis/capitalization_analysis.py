import json
import re
from pathlib import Path


BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "capitalization_analysis.json"


# ---------------------------------------------------------
# LOAD MESSAGES
# ---------------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


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
            "alphabetic_characters": 0,
            "uppercase_characters": 0,
            "lowercase_characters": 0,
            "all_uppercase_messages": 0,
            "mixed_case_messages": 0,
        }

    data = speaker_data[sender]

    data["messages_analyzed"] += 1

    # Only alphabetic characters
    letters = re.findall(r"[A-Za-z]", text)

    if not letters:
        continue

    uppercase_count = sum(
        1 for char in letters
        if char.isupper()
    )

    lowercase_count = sum(
        1 for char in letters
        if char.islower()
    )

    data["alphabetic_characters"] += len(letters)
    data["uppercase_characters"] += uppercase_count
    data["lowercase_characters"] += lowercase_count

    # -----------------------------------------------------
    # ALL-UPPERCASE MESSAGE
    # -----------------------------------------------------

    if (
        uppercase_count > 0
        and uppercase_count == len(letters)
    ):
        data["all_uppercase_messages"] += 1

    # -----------------------------------------------------
    # MIXED CASE MESSAGE
    # -----------------------------------------------------

    elif uppercase_count > 0 and lowercase_count > 0:
        data["mixed_case_messages"] += 1


# ---------------------------------------------------------
# BUILD PROFILE
# ---------------------------------------------------------

profile = {}


for speaker, data in speaker_data.items():

    total_letters = data["alphabetic_characters"]
    total_messages = data["messages_analyzed"]

    if total_letters > 0:

        uppercase_percentage = (
            data["uppercase_characters"]
            / total_letters
        ) * 100

        lowercase_percentage = (
            data["lowercase_characters"]
            / total_letters
        ) * 100

    else:

        uppercase_percentage = 0
        lowercase_percentage = 0


    if total_messages > 0:

        all_uppercase_percentage = (
            data["all_uppercase_messages"]
            / total_messages
        ) * 100

        mixed_case_percentage = (
            data["mixed_case_messages"]
            / total_messages
        ) * 100

    else:

        all_uppercase_percentage = 0
        mixed_case_percentage = 0


    profile[speaker] = {

        "messages_analyzed":
            total_messages,

        "alphabetic_characters":
            total_letters,

        "uppercase_characters":
            data["uppercase_characters"],

        "lowercase_characters":
            data["lowercase_characters"],

        "uppercase_percentage":
            round(
                uppercase_percentage,
                2
            ),

        "lowercase_percentage":
            round(
                lowercase_percentage,
                2
            ),

        "all_uppercase_messages":
            data["all_uppercase_messages"],

        "all_uppercase_message_percentage":
            round(
                all_uppercase_percentage,
                2
            ),

        "mixed_case_messages":
            data["mixed_case_messages"],

        "mixed_case_message_percentage":
            round(
                mixed_case_percentage,
                2
            ),
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

print("\n========== CAPITALIZATION ANALYSIS ==========\n")


for speaker, data in profile.items():

    print(f"Speaker: {speaker}")

    print(
        f"  Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print(
        f"  Alphabetic characters: "
        f"{data['alphabetic_characters']}"
    )

    print(
        f"  Uppercase characters: "
        f"{data['uppercase_characters']}"
    )

    print(
        f"  Lowercase characters: "
        f"{data['lowercase_characters']}"
    )

    print(
        f"  Uppercase percentage: "
        f"{data['uppercase_percentage']}%"
    )

    print(
        f"  Lowercase percentage: "
        f"{data['lowercase_percentage']}%"
    )

    print(
        f"  ALL-UPPERCASE messages: "
        f"{data['all_uppercase_messages']}"
    )

    print(
        f"  ALL-UPPERCASE percentage: "
        f"{data['all_uppercase_message_percentage']}%"
    )

    print(
        f"  Mixed-case messages: "
        f"{data['mixed_case_messages']}"
    )

    print(
        f"  Mixed-case percentage: "
        f"{data['mixed_case_message_percentage']}%"
    )

    print()


print("Saved to:")
print(OUTPUT_FILE)