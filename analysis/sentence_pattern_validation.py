import json
import re
from pathlib import Path


BASE = Path("data/processed")

MESSAGES_FILE = BASE / "messages.json"

SENTENCE_FILE = BASE / "sentence_patterns.json"
MESSAGE_FILE = BASE / "message_length_patterns.json"
QUESTION_FILE = BASE / "question_analysis.json"
EXCLAMATION_FILE = BASE / "exclamation_analysis.json"
PUNCTUATION_FILE = BASE / "punctuation_analysis.json"
CAPITALIZATION_FILE = BASE / "capitalization_analysis.json"
EXPRESSION_FILE = BASE / "message_expression_patterns.json"

OUTPUT_FILE = BASE / "sentence_pattern_validation.json"


# ---------------------------------------------------------
# LOAD JSON
# ---------------------------------------------------------

def load_json(path):
    if not path.exists():
        print(f"⚠️ Missing: {path}")
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


messages = load_json(MESSAGES_FILE)
sentence_data = load_json(SENTENCE_FILE)
message_data = load_json(MESSAGE_FILE)
question_data = load_json(QUESTION_FILE)
exclamation_data = load_json(EXCLAMATION_FILE)
punctuation_data = load_json(PUNCTUATION_FILE)
capitalization_data = load_json(CAPITALIZATION_FILE)
expression_data = load_json(EXPRESSION_FILE)


# ---------------------------------------------------------
# SPEAKERS
# ---------------------------------------------------------

speakers = list(sentence_data.keys())

if len(speakers) < 2:
    print("❌ Need at least two speakers for comparison.")
    raise SystemExit


# ---------------------------------------------------------
# COLLECT EXAMPLES
# ---------------------------------------------------------

examples = {}

for speaker in speakers:

    examples[speaker] = {
        "short_messages": [],
        "long_messages": [],
        "questions": [],
        "exclamations": [],
        "repeated_punctuation": [],
    }


for message in messages:

    sender = message.get("sender")
    text = message.get("message")

    if sender not in examples:
        continue

    if not text:
        continue

    if message.get("is_deleted"):
        continue

    if message.get("is_media"):
        continue

    text = text.strip()

    if not text:
        continue

    word_count = len(text.split())


    # -----------------------------------------------------
    # SHORT MESSAGE
    # -----------------------------------------------------

    if word_count <= 3:

        if len(examples[sender]["short_messages"]) < 10:

            examples[sender]["short_messages"].append(text)


    # -----------------------------------------------------
    # LONG MESSAGE
    # -----------------------------------------------------

    if word_count >= 30:

        if len(examples[sender]["long_messages"]) < 10:

            examples[sender]["long_messages"].append(text)


    # -----------------------------------------------------
    # QUESTIONS
    # -----------------------------------------------------

    if "?" in text:

        if len(examples[sender]["questions"]) < 10:

            examples[sender]["questions"].append(text)


    # -----------------------------------------------------
    # EXCLAMATIONS
    # -----------------------------------------------------

    if "!" in text:

        if len(examples[sender]["exclamations"]) < 10:

            examples[sender]["exclamations"].append(text)


    # -----------------------------------------------------
    # REPEATED PUNCTUATION
    # -----------------------------------------------------

    if re.search(r"[!?.,]{2,}", text):

        if len(
            examples[sender]["repeated_punctuation"]
        ) < 10:

            examples[sender][
                "repeated_punctuation"
            ].append(text)


# ---------------------------------------------------------
# WHATSAPP EXPORT ARTIFACT DETECTION
# ---------------------------------------------------------

ARTIFACT_PATTERNS = [

    r"Messages and calls are end-to-end encrypted",

    r"This message was deleted",

    r"You deleted this message",

    r"<Media omitted>",

    r"image omitted",

    r"video omitted",

    r"audio omitted",

    r"sticker omitted",

]


artifact_examples = []


for message in messages:

    text = message.get("message")

    if not text:
        continue

    for pattern in ARTIFACT_PATTERNS:

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            artifact_examples.append({
                "message": text,
                "matched_pattern": pattern,
            })

            break


# ---------------------------------------------------------
# COMPARE SPEAKERS
# ---------------------------------------------------------

comparison = {}


for speaker in speakers:

    comparison[speaker] = {

        "average_sentence_length":
            sentence_data
            .get(speaker, {})
            .get(
                "average_sentence_length",
                0
            ),

        "average_words_per_message":
            message_data
            .get(speaker, {})
            .get(
                "average_words_per_message",
                0
            ),

        "question_percentage":
            question_data
            .get(speaker, {})
            .get(
                "question_percentage",
                0
            ),

        "exclamation_percentage":
            exclamation_data
            .get(speaker, {})
            .get(
                "exclamation_percentage",
                0
            ),

        "punctuation_per_message":
            punctuation_data
            .get(speaker, {})
            .get(
                "punctuation_marks_per_message",
                0
            ),

        "uppercase_percentage":
            capitalization_data
            .get(speaker, {})
            .get(
                "uppercase_percentage",
                0
            ),

        "multi_sentence_percentage":
            sentence_data
            .get(speaker, {})
            .get(
                "multi_sentence_message_percentage",
                0
            ),

        "message_continuation_percentage":
            expression_data
            .get(speaker, {})
            .get(
                "possible_continuation_percentage",
                0
            ),
    }


# ---------------------------------------------------------
# DIFFERENCES
# ---------------------------------------------------------

differences = {}


if len(speakers) >= 2:

    speaker_a = speakers[0]
    speaker_b = speakers[1]

    differences = {

        "average_sentence_length_difference":
            round(
                comparison[speaker_a][
                    "average_sentence_length"
                ]
                -
                comparison[speaker_b][
                    "average_sentence_length"
                ],
                2
            ),

        "average_message_length_difference":
            round(
                comparison[speaker_a][
                    "average_words_per_message"
                ]
                -
                comparison[speaker_b][
                    "average_words_per_message"
                ],
                2
            ),

        "question_percentage_difference":
            round(
                comparison[speaker_a][
                    "question_percentage"
                ]
                -
                comparison[speaker_b][
                    "question_percentage"
                ],
                2
            ),

        "exclamation_percentage_difference":
            round(
                comparison[speaker_a][
                    "exclamation_percentage"
                ]
                -
                comparison[speaker_b][
                    "exclamation_percentage"
                ],
                2
            ),

        "uppercase_percentage_difference":
            round(
                comparison[speaker_a][
                    "uppercase_percentage"
                ]
                -
                comparison[speaker_b][
                    "uppercase_percentage"
                ],
                2
            ),
    }


# ---------------------------------------------------------
# FINAL RESULT
# ---------------------------------------------------------

result = {

    "speakers": speakers,

    "speaker_comparison": comparison,

    "speaker_differences": differences,

    "example_messages": examples,

    "whatsapp_export_artifacts": {

        "artifact_count":
            len(artifact_examples),

        "examples":
            artifact_examples[:20],
    },

    "validation_notes": [

        "Compare both speakers before treating a pattern as distinctive.",

        "Inspect real message examples before interpreting a numerical pattern.",

        "Do not treat WhatsApp system/export messages as personal communication style.",

        "Very small frequency differences should not be treated as strong style signals.",

        "Sentence and message statistics describe communication behavior, not personality by themselves.",
    ],
}


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        result,
        file,
        ensure_ascii=False,
        indent=2
    )


# ---------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------

print("\n========== DAY 5 VALIDATION ==========\n")

print("Speakers:")

for speaker in speakers:
    print(f"  ✓ {speaker}")


print("\n========== SPEAKER COMPARISON ==========\n")

for speaker, data in comparison.items():

    print(f"Speaker: {speaker}")

    print(
        f"  Average sentence length: "
        f"{data['average_sentence_length']}"
    )

    print(
        f"  Average message length: "
        f"{data['average_words_per_message']}"
    )

    print(
        f"  Question percentage: "
        f"{data['question_percentage']}%"
    )

    print(
        f"  Exclamation percentage: "
        f"{data['exclamation_percentage']}%"
    )

    print(
        f"  Punctuation/message: "
        f"{data['punctuation_per_message']}"
    )

    print(
        f"  Uppercase percentage: "
        f"{data['uppercase_percentage']}%"
    )

    print(
        f"  Multi-sentence messages: "
        f"{data['multi_sentence_percentage']}%"
    )

    print(
        f"  Possible message continuations: "
        f"{data['message_continuation_percentage']}%"
    )

    print()


print("========== WHATSAPP ARTIFACTS ==========\n")

print(
    f"Potential export artifacts: "
    f"{len(artifact_examples)}"
)

for artifact in artifact_examples[:10]:

    print(
        f"  - {artifact['message']}"
    )


print("\n========== VALIDATION COMPLETE ==========\n")

print("✓ Speaker comparison generated")
print("✓ Real message examples collected")
print("✓ WhatsApp artifacts checked")
print("✓ Day 5 sentence/message profile validated")

print("\nSaved to:")
print(OUTPUT_FILE)