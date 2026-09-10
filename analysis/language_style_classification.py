import json
import re
from collections import Counter, defaultdict
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

MESSAGES_FILE = PROCESSED_DIR / "messages.json"
TAMIL_FILE = PROCESSED_DIR / "tamil_script_detection.json"
TANGLISH_FILE = PROCESSED_DIR / "tanglish_vocabulary_detection.json"

OUTPUT_FILE = PROCESSED_DIR / "language_style_classification.json"


# ============================================================
# CONFIG
# ============================================================

MAX_EXAMPLES_PER_CATEGORY = 10

# Tanglish classification thresholds
MIN_TANGLISH_WORDS = 2
TANGLISH_RATIO_THRESHOLD = 0.20

# Tamil-script threshold
MIN_TAMIL_CHARS = 2
TAMIL_RATIO_THRESHOLD = 0.20


# ============================================================
# HELPERS
# ============================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def tokenize_english_script(text):
    return re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text.lower())


def tamil_characters(text):
    return re.findall(r"[\u0B80-\u0BFF]", text)


def is_valid_message(item):
    sender = item.get("sender")
    message = item.get("message")

    if not sender:
        return False

    if not message:
        return False

    message = message.strip()

    if not message:
        return False

    deleted_markers = {
        "You deleted this message",
        "This message was deleted",
    }

    if message in deleted_markers:
        return False

    return True


def safe_percentage(part, total):
    if total == 0:
        return 0.0

    return round((part / total) * 100, 2)


# ============================================================
# LOAD DATA
# ============================================================

messages = load_json(MESSAGES_FILE)
tamil_data = load_json(TAMIL_FILE)
tanglish_data = load_json(TANGLISH_FILE)


# ============================================================
# INDEX EXISTING ANALYSIS
# ============================================================

tamil_by_id = {}

for item in tamil_data.get("messages", []):
    tamil_by_id[item["id"]] = item


tanglish_by_id = {}

for item in tanglish_data.get("messages", []):
    tanglish_by_id[item["id"]] = item


# ============================================================
# CLASSIFICATION
# ============================================================

speaker_stats = defaultdict(lambda: {
    "total_messages": 0,
    "english": 0,
    "tamil_script": 0,
    "tanglish": 0,
    "mixed_english_tanglish": 0,
    "mixed_tamil_english": 0,
    "mixed_tamil_tanglish": 0,
    "mixed_all": 0,
    "unknown": 0,
})


category_examples = defaultdict(list)

message_results = []


for item in messages:

    if not is_valid_message(item):
        continue

    message_id = item["id"]
    sender = item["sender"]
    text = item["message"].strip()

    # --------------------------------------------------------
    # Tamil script statistics
    # --------------------------------------------------------

    tamil_chars = tamil_characters(text)
    tamil_count = len(tamil_chars)

    total_alpha_chars = len(
        re.findall(r"[A-Za-z\u0B80-\u0BFF]", text)
    )

    tamil_ratio = (
        tamil_count / total_alpha_chars
        if total_alpha_chars > 0
        else 0
    )

    has_tamil_script = (
        tamil_count >= MIN_TAMIL_CHARS
        and tamil_ratio >= TAMIL_RATIO_THRESHOLD
    )

    # --------------------------------------------------------
    # English-script statistics
    # --------------------------------------------------------

    words = tokenize_english_script(text)
    english_word_count = len(words)

    # --------------------------------------------------------
    # Tanglish statistics
    # --------------------------------------------------------

    tanglish_info = tanglish_by_id.get(message_id, {})

    tanglish_words = tanglish_info.get(
        "tanglish_words",
        []
    )

    tanglish_count = len(tanglish_words)

    tanglish_ratio = (
        tanglish_count / english_word_count
        if english_word_count > 0
        else 0
    )

    has_tanglish = (
        tanglish_count >= MIN_TANGLISH_WORDS
        and tanglish_ratio >= TANGLISH_RATIO_THRESHOLD
    )

    # --------------------------------------------------------
    # Estimate English words
    # --------------------------------------------------------

    english_count = max(
        english_word_count - tanglish_count,
        0
    )

    has_english = english_count > 0

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    if has_tamil_script and has_tanglish and has_english:
        category = "mixed_all"

    elif has_tamil_script and has_english:
        category = "mixed_tamil_english"

    elif has_tamil_script and has_tanglish:
        category = "mixed_tamil_tanglish"

    elif has_tamil_script:
        category = "tamil_script"

    elif has_tanglish and has_english:
        category = "mixed_english_tanglish"

    elif has_tanglish:
        category = "tanglish"

    elif has_english:
        category = "english"

    else:
        category = "unknown"

    # --------------------------------------------------------
    # Speaker statistics
    # --------------------------------------------------------

    speaker_stats[sender]["total_messages"] += 1
    speaker_stats[sender][category] += 1

    # --------------------------------------------------------
    # Examples
    # --------------------------------------------------------

    if len(category_examples[category]) < MAX_EXAMPLES_PER_CATEGORY:
        category_examples[category].append({
            "id": message_id,
            "sender": sender,
            "message": text
        })

    # --------------------------------------------------------
    # Store message result
    # --------------------------------------------------------

    message_results.append({
        "id": message_id,
        "sender": sender,
        "message": text,
        "classification": category,
        "signals": {
            "tamil_char_count": tamil_count,
            "tamil_ratio": round(tamil_ratio, 3),
            "english_word_count": english_word_count,
            "english_word_count_estimated": english_count,
            "tanglish_word_count": tanglish_count,
            "tanglish_ratio": round(tanglish_ratio, 3),
            "has_tamil_script": has_tamil_script,
            "has_tanglish": has_tanglish,
            "has_english": has_english
        }
    })


# ============================================================
# BUILD SPEAKER PROFILES
# ============================================================

speaker_profiles = {}

for speaker, stats in speaker_stats.items():

    total = stats["total_messages"]

    percentages = {}

    for category in [
        "english",
        "tamil_script",
        "tanglish",
        "mixed_english_tanglish",
        "mixed_tamil_english",
        "mixed_tamil_tanglish",
        "mixed_all",
        "unknown"
    ]:
        percentages[category] = safe_percentage(
            stats[category],
            total
        )

    speaker_profiles[speaker] = {
        "total_messages": total,
        "counts": dict(stats),
        "percentages": percentages
    }


# ============================================================
# OVERALL PROFILE
# ============================================================

overall_counts = Counter()

for result in message_results:
    overall_counts[result["classification"]] += 1


overall_total = len(message_results)

overall_percentages = {}

for category in [
    "english",
    "tamil_script",
    "tanglish",
    "mixed_english_tanglish",
    "mixed_tamil_english",
    "mixed_tamil_tanglish",
    "mixed_all",
    "unknown"
]:
    overall_percentages[category] = safe_percentage(
        overall_counts[category],
        overall_total
    )


# ============================================================
# SAVE OUTPUT
# ============================================================

output = {
    "analysis": "Language Style Classification",
    "description": (
        "Heuristic classification of messages into English, "
        "Tamil script, Tanglish, and mixed-language categories."
    ),

    "classification_rules": {
        "tamil_script": {
            "minimum_tamil_characters": MIN_TAMIL_CHARS,
            "minimum_tamil_ratio": TAMIL_RATIO_THRESHOLD
        },
        "tanglish": {
            "minimum_tanglish_words": MIN_TANGLISH_WORDS,
            "minimum_tanglish_ratio": TANGLISH_RATIO_THRESHOLD
        }
    },

    "overall": {
        "total_messages": overall_total,
        "counts": dict(overall_counts),
        "percentages": overall_percentages
    },

    "speaker_profiles": speaker_profiles,

    "category_examples": dict(category_examples),

    "messages": message_results
}


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        output,
        f,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# CONSOLE OUTPUT
# ============================================================

print("\n========== LANGUAGE STYLE CLASSIFICATION ==========\n")

print(f"Messages analyzed: {overall_total}")

print("\nOverall:")

for category, count in overall_counts.most_common():
    percentage = safe_percentage(count, overall_total)
    print(
        f"  {category:<28} "
        f"{count:>6} ({percentage:>6}%)"
    )


print("\nSpeaker Profiles:")

for speaker, profile in speaker_profiles.items():

    print(f"\n--- {speaker} ---")

    total = profile["total_messages"]

    print(f"Total messages: {total}")

    for category, count in profile["counts"].items():

        if category == "total_messages":
            continue

        percentage = profile["percentages"][category]

        if count > 0:
            print(
                f"  {category:<28} "
                f"{count:>6} ({percentage:>6}%)"
            )


print("\nExamples:")

for category, examples in category_examples.items():

    print(f"\n[{category}]")

    for example in examples[:3]:
        print(
            f"  {example['sender']}: "
            f"{example['message'][:120]}"
        )


print("\nSaved:")
print(OUTPUT_FILE)