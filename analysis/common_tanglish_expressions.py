import json
import re
from collections import Counter
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "tanglish_vocabulary_detection.json"
OUTPUT_FILE = PROCESSED_DIR / "common_tanglish_expressions.json"


# ============================================================
# CONFIG
# ============================================================

MIN_COUNT = 3
MAX_RESULTS = 50
MAX_EXAMPLES = 5


# ============================================================
# COMMON ENGLISH / AMBIGUOUS WORDS
# ============================================================

EXCLUDED_WORDS = {
    "okay",
    "ok",
    "but",
    "because",
    "super",
    "fine",
    "yes",
    "no",
    "hi",
    "hello",
    "bye",
    "good",
    "bad",
    "nice",
    "really",
    "very",
    "just",
    "only",
    "also",
    "and",
    "or",
    "so",
    "if",
    "then",
    "with",
    "from",
    "for",
    "the",
    "this",
    "that",
    "what",
    "when",
    "where",
    "why",
    "how",
}


# ============================================================
# LOAD
# ============================================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


speakers = data.get("speakers", {})


# ============================================================
# BUILD PROFILES
# ============================================================

speaker_profiles = {}


for speaker, profile in speakers.items():

    raw_words = profile.get(
        "top_tanglish_words",
        []
    )

    filtered_words = []

    for item in raw_words:

        word = item.get("word", "").lower().strip()
        count = item.get("count", 0)

        if not word:
            continue

        if count < MIN_COUNT:
            continue

        if word in EXCLUDED_WORDS:
            continue

        filtered_words.append({
            "expression": word,
            "count": count
        })

    # Sort by frequency
    filtered_words.sort(
        key=lambda x: x["count"],
        reverse=True
    )

    # --------------------------------------------------------
    # Examples
    # --------------------------------------------------------

    examples = profile.get("examples", [])

    word_examples = {}

    for example in examples:

        message = example.get("message", "")

        for word in example.get(
            "tanglish_words",
            []
        ):

            word = word.lower()

            if word in EXCLUDED_WORDS:
                continue

            if word not in word_examples:
                word_examples[word] = []

            if (
                len(word_examples[word])
                < MAX_EXAMPLES
            ):
                word_examples[word].append(message)

    # Attach examples
    for item in filtered_words:

        word = item["expression"]

        item["examples"] = word_examples.get(
            word,
            []
        )

    speaker_profiles[speaker] = {
        "messages_analyzed": profile.get(
            "messages_analyzed",
            0
        ),

        "messages_with_tanglish": profile.get(
            "messages_with_tanglish",
            0
        ),

        "tanglish_message_percentage": profile.get(
            "tanglish_message_percentage",
            0
        ),

        "total_tanglish_words": profile.get(
            "total_tanglish_words",
            0
        ),

        "unique_tanglish_words": profile.get(
            "unique_tanglish_words",
            0
        ),

        "filtered_common_expressions": (
            filtered_words[:MAX_RESULTS]
        )
    }


# ============================================================
# CROSS-SPEAKER COMPARISON
# ============================================================

speaker_names = list(speaker_profiles.keys())

shared = []
speaker_specific = {}


if len(speaker_names) >= 2:

    speaker_a = speaker_names[0]
    speaker_b = speaker_names[1]

    words_a = {
        item["expression"]: item["count"]
        for item in speaker_profiles[
            speaker_a
        ]["filtered_common_expressions"]
    }

    words_b = {
        item["expression"]: item["count"]
        for item in speaker_profiles[
            speaker_b
        ]["filtered_common_expressions"]
    }

    # --------------------------------------------------------
    # Shared
    # --------------------------------------------------------

    for word in set(words_a) & set(words_b):

        shared.append({
            "expression": word,
            speaker_a: words_a[word],
            speaker_b: words_b[word],
            "total": (
                words_a[word]
                + words_b[word]
            )
        })

    shared.sort(
        key=lambda x: x["total"],
        reverse=True
    )

    # --------------------------------------------------------
    # Speaker specific
    # --------------------------------------------------------

    speaker_specific[speaker_a] = [
        {
            "expression": word,
            "count": count
        }
        for word, count in words_a.items()
        if word not in words_b
    ]

    speaker_specific[speaker_b] = [
        {
            "expression": word,
            "count": count
        }
        for word, count in words_b.items()
        if word not in words_a
    ]


# ============================================================
# SAVE
# ============================================================

output = {
    "analysis": "Common Tanglish Expressions",

    "description": (
        "Frequently occurring Tanglish vocabulary "
        "after removing obvious English and ambiguous terms."
    ),

    "configuration": {
        "minimum_count": MIN_COUNT,
        "excluded_words_count": len(EXCLUDED_WORDS)
    },

    "speaker_profiles": speaker_profiles,

    "shared_expressions": shared[:MAX_RESULTS],

    "speaker_specific_expressions": speaker_specific
}


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    json.dump(
        output,
        f,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# OUTPUT
# ============================================================

print("\n========== COMMON TANGLISH EXPRESSIONS ==========\n")


for speaker, profile in speaker_profiles.items():

    print(f"\n--- {speaker} ---")

    print(
        f"Messages with Tanglish: "
        f"{profile['messages_with_tanglish']} "
        f"({profile['tanglish_message_percentage']}%)"
    )

    print(
        f"Total detected Tanglish words: "
        f"{profile['total_tanglish_words']}"
    )

    print(
        f"Unique detected Tanglish words: "
        f"{profile['unique_tanglish_words']}"
    )

    print("\nFiltered common expressions:")

    for item in profile[
        "filtered_common_expressions"
    ][:20]:

        print(
            f"  {item['expression']:<15}"
            f"{item['count']:>5}"
        )


if shared:

    print("\n--- SHARED TANGLISH ---")

    for item in shared[:20]:

        print(
            f"  {item['expression']:<15}"
            f"{item['total']:>5}"
        )


print("\nSaved:")
print(OUTPUT_FILE)