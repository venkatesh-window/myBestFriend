import json
import re
from pathlib import Path


BASE = Path("data/processed")

INPUT_FILE = BASE / "messages.json"
OUTPUT_FILE = BASE / "question_analysis.json"


# ---------------------------------------------------------
# LOAD MESSAGES
# ---------------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# ---------------------------------------------------------
# QUESTION DETECTION
# ---------------------------------------------------------

def contains_question(text):
    """
    Detect whether a message contains a question.

    Primary signal:
        ?

    Secondary signal:
        common question words at the beginning
    """

    if "?" in text:
        return True

    question_pattern = re.compile(
        r"^\s*(who|what|when|where|why|how|which|"
        r"can|could|would|will|do|does|did|is|are|"
        r"am|was|were|have|has|should)\b",
        re.IGNORECASE
    )

    return bool(question_pattern.search(text))


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
            "question_messages": 0,
            "question_marks": 0,
            "messages_with_multiple_questions": 0,
        }

    data = speaker_data[sender]

    data["messages_analyzed"] += 1

    # Count question marks
    question_marks = text.count("?")

    data["question_marks"] += question_marks

    # Detect question message
    if contains_question(text):

        data["question_messages"] += 1

    # Multiple question marks
    if question_marks > 1:

        data["messages_with_multiple_questions"] += 1


# ---------------------------------------------------------
# BUILD PROFILE
# ---------------------------------------------------------

profile = {}


for speaker, data in speaker_data.items():

    total_messages = data["messages_analyzed"]

    if total_messages > 0:

        question_percentage = (
            data["question_messages"]
            / total_messages
        ) * 100

        question_marks_per_message = (
            data["question_marks"]
            / total_messages
        )

    else:

        question_percentage = 0
        question_marks_per_message = 0

    profile[speaker] = {

        "messages_analyzed": total_messages,

        "question_messages":
            data["question_messages"],

        "question_percentage": round(
            question_percentage,
            2
        ),

        "total_question_marks":
            data["question_marks"],

        "question_marks_per_message": round(
            question_marks_per_message,
            3
        ),

        "messages_with_multiple_questions":
            data["messages_with_multiple_questions"],
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

print("\n========== QUESTION ANALYSIS ==========\n")


for speaker, data in profile.items():

    print(f"Speaker: {speaker}")

    print(
        f"  Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print(
        f"  Question messages: "
        f"{data['question_messages']}"
    )

    print(
        f"  Question percentage: "
        f"{data['question_percentage']}%"
    )

    print(
        f"  Total question marks: "
        f"{data['total_question_marks']}"
    )

    print(
        f"  Question marks/message: "
        f"{data['question_marks_per_message']}"
    )

    print(
        f"  Messages with multiple questions: "
        f"{data['messages_with_multiple_questions']}"
    )

    print()


print("Saved to:")
print(OUTPUT_FILE)