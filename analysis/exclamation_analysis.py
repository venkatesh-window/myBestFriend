import json
from pathlib import Path


BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "exclamation_analysis.json"


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
            "messages_with_exclamation": 0,
            "total_exclamation_marks": 0,
            "multiple_exclamation_messages": 0,
        }

    data = speaker_data[sender]

    data["messages_analyzed"] += 1

    # Count !
    exclamation_count = text.count("!")

    data["total_exclamation_marks"] += exclamation_count

    # Message contains at least one !
    if exclamation_count > 0:

        data["messages_with_exclamation"] += 1

    # Message contains multiple !
    if exclamation_count > 1:

        data["multiple_exclamation_messages"] += 1


# ---------------------------------------------------------
# BUILD PROFILE
# ---------------------------------------------------------

profile = {}


for speaker, data in speaker_data.items():

    total_messages = data["messages_analyzed"]

    if total_messages > 0:

        exclamation_percentage = (
            data["messages_with_exclamation"]
            / total_messages
        ) * 100

        exclamations_per_message = (
            data["total_exclamation_marks"]
            / total_messages
        )

    else:

        exclamation_percentage = 0
        exclamations_per_message = 0

    profile[speaker] = {

        "messages_analyzed": total_messages,

        "messages_with_exclamation":
            data["messages_with_exclamation"],

        "exclamation_percentage": round(
            exclamation_percentage,
            2
        ),

        "total_exclamation_marks":
            data["total_exclamation_marks"],

        "exclamations_per_message": round(
            exclamations_per_message,
            3
        ),

        "messages_with_multiple_exclamations":
            data["multiple_exclamation_messages"],
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

print("\n========== EXCLAMATION ANALYSIS ==========\n")


for speaker, data in profile.items():

    print(f"Speaker: {speaker}")

    print(
        f"  Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print(
        f"  Messages with !: "
        f"{data['messages_with_exclamation']}"
    )

    print(
        f"  Exclamation percentage: "
        f"{data['exclamation_percentage']}%"
    )

    print(
        f"  Total ! marks: "
        f"{data['total_exclamation_marks']}"
    )

    print(
        f"  Exclamations/message: "
        f"{data['exclamations_per_message']}"
    )

    print(
        f"  Messages with multiple !: "
        f"{data['messages_with_multiple_exclamations']}"
    )

    print()


print("Saved to:")
print(OUTPUT_FILE)