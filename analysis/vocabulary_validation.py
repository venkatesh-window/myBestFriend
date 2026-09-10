import json
from pathlib import Path
from collections import Counter

BASE = Path("data/processed")

DISTINCTIVE_FILE = BASE / "distinctive_words.json"
COMMON_FILE = BASE / "common_vs_distinctive.json"
DIVERSITY_FILE = BASE / "vocabulary_diversity.json"

OUTPUT_FILE = BASE / "vocabulary_validation.json"


# ---------------------------------------------------------
# LOAD JSON
# ---------------------------------------------------------

def load_json(path):
    if not path.exists():
        print(f"⚠️ Missing: {path}")
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


distinctive = load_json(DISTINCTIVE_FILE)
common = load_json(COMMON_FILE)
diversity = load_json(DIVERSITY_FILE)


if distinctive is None or common is None or diversity is None:
    print("\n❌ Required analysis files are missing.")
    print("Run the previous Day 4 analysis scripts first.")
    raise SystemExit


# ---------------------------------------------------------
# GENERIC WORDS
# ---------------------------------------------------------

GENERIC_WORDS = {
    "i", "me", "my", "you", "your", "we", "our", "they", "them",
    "he", "she", "it", "this", "that", "these", "those",

    "a", "an", "the",
    "and", "or", "but", "so", "because",
    "if", "then", "than",

    "is", "am", "are", "was", "were", "be", "been",
    "do", "does", "did",
    "have", "has", "had",

    "in", "on", "at", "to", "for", "from", "with",
    "of", "by", "as",

    "what", "when", "where", "who", "why", "how",

    "yes", "no", "okay", "ok",
    "yeah", "ya", "hey", "hi",

    "very", "really", "just", "now", "then",
}


# ---------------------------------------------------------
# VALIDATE DISTINCTIVE WORDS
# ---------------------------------------------------------

validated = {}

for speaker, words in distinctive.items():

    validated[speaker] = {
        "useful_words": [],
        "generic_words_removed": [],
        "low_frequency_words_removed": [],
    }

    for item in words:

        word = item.get("word")
        count = item.get("count", 0)
        score = item.get("distinctiveness_score", 0)

        if not word:
            continue

        normalized_word = word.lower()

        # Remove very rare words
        if count < 3:
            validated[speaker]["low_frequency_words_removed"].append({
                "word": word,
                "count": count,
                "score": score
            })
            continue

        # Remove obvious generic words
        if normalized_word in GENERIC_WORDS:
            validated[speaker]["generic_words_removed"].append({
                "word": word,
                "count": count,
                "score": score
            })
            continue

        # Keep useful candidate
        validated[speaker]["useful_words"].append({
            "word": word,
            "count": count,
            "score": score
        })


# ---------------------------------------------------------
# SPEAKER COMPARISON
# ---------------------------------------------------------

speaker_comparison = {}

for speaker, data in diversity.items():

    speaker_comparison[speaker] = {
        "total_words": data.get("total_words", 0),
        "unique_words": data.get("unique_words", 0),
        "type_token_ratio": data.get("type_token_ratio", 0),
        "vocabulary_diversity_percentage": data.get(
            "vocabulary_diversity_percentage", 0
        ),
        "words_used_only_once": data.get(
            "words_used_only_once", 0
        ),
    }


# ---------------------------------------------------------
# VALIDATION SUMMARY
# ---------------------------------------------------------

summary = {}

for speaker, data in validated.items():

    useful_count = len(data["useful_words"])
    generic_count = len(data["generic_words_removed"])
    low_frequency_count = len(data["low_frequency_words_removed"])

    summary[speaker] = {
        "useful_distinctive_words": useful_count,
        "generic_words_removed": generic_count,
        "low_frequency_words_removed": low_frequency_count,
    }


# ---------------------------------------------------------
# FINAL RESULT
# ---------------------------------------------------------

result = {
    "validation_summary": summary,
    "speaker_comparison": speaker_comparison,
    "validated_distinctive_vocabulary": validated,
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

print("\n========== VOCABULARY VALIDATION ==========\n")

for speaker, data in validated.items():

    print(f"Speaker: {speaker}")

    print(
        f"  ✓ Useful distinctive words: "
        f"{len(data['useful_words'])}"
    )

    print(
        f"  ✓ Generic words removed: "
        f"{len(data['generic_words_removed'])}"
    )

    print(
        f"  ✓ Low-frequency words removed: "
        f"{len(data['low_frequency_words_removed'])}"
    )

    print("\n  Top useful words:")

    for item in data["useful_words"][:15]:
        print(
            f"    {item['word']} "
            f"(count={item['count']}, "
            f"score={item['score']:.2f})"
        )

    print("\n")


print("========== SPEAKER COMPARISON ==========\n")

for speaker, data in speaker_comparison.items():

    print(f"Speaker: {speaker}")
    print(f"  Total words: {data['total_words']}")
    print(f"  Unique words: {data['unique_words']}")
    print(f"  TTR: {data['type_token_ratio']:.4f}")
    print(
        f"  Diversity: "
        f"{data['vocabulary_diversity_percentage']:.2f}%"
    )
    print(
        f"  Words used only once: "
        f"{data['words_used_only_once']}"
    )
    print()


print("Saved to:")
print(OUTPUT_FILE)