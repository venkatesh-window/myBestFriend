import json
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "language_style_classification.json"
OUTPUT_FILE = PROCESSED_DIR / "speaker_language_profile.json"


# ============================================================
# LOAD DATA
# ============================================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


speaker_profiles = data.get("speaker_profiles", {})


# ============================================================
# BUILD LANGUAGE PROFILE
# ============================================================

language_categories = [
    "english",
    "tamil_script",
    "tanglish",
    "mixed_english_tanglish",
    "mixed_tamil_english",
    "mixed_tamil_tanglish",
    "mixed_all",
    "unknown"
]


output_profiles = {}


for speaker, profile in speaker_profiles.items():

    total = profile.get("total_messages", 0)
    counts = profile.get("counts", {})
    percentages = profile.get("percentages", {})

    # --------------------------------------------------------
    # Main language
    # --------------------------------------------------------

    main_candidates = {
        category: counts.get(category, 0)
        for category in language_categories
        if category != "unknown"
    }

    main_language = (
        max(main_candidates, key=main_candidates.get)
        if main_candidates
        else "unknown"
    )

    # --------------------------------------------------------
    # English usage
    # --------------------------------------------------------

    english_messages = (
        counts.get("english", 0)
        + counts.get("mixed_english_tanglish", 0)
        + counts.get("mixed_tamil_english", 0)
        + counts.get("mixed_all", 0)
    )

    # --------------------------------------------------------
    # Tanglish usage
    # --------------------------------------------------------

    tanglish_messages = (
        counts.get("tanglish", 0)
        + counts.get("mixed_english_tanglish", 0)
        + counts.get("mixed_tamil_tanglish", 0)
        + counts.get("mixed_all", 0)
    )

    # --------------------------------------------------------
    # Tamil-script usage
    # --------------------------------------------------------

    tamil_script_messages = (
        counts.get("tamil_script", 0)
        + counts.get("mixed_tamil_english", 0)
        + counts.get("mixed_tamil_tanglish", 0)
        + counts.get("mixed_all", 0)
    )

    # --------------------------------------------------------
    # Mixed-language usage
    # --------------------------------------------------------

    mixed_messages = (
        counts.get("mixed_english_tanglish", 0)
        + counts.get("mixed_tamil_english", 0)
        + counts.get("mixed_tamil_tanglish", 0)
        + counts.get("mixed_all", 0)
    )

    # --------------------------------------------------------
    # Percentages
    # --------------------------------------------------------

    def percentage(value):
        if total == 0:
            return 0.0

        return round((value / total) * 100, 2)

    # --------------------------------------------------------
    # Profile
    # --------------------------------------------------------

    output_profiles[speaker] = {

        "total_messages": total,

        "dominant_message_language": main_language,

        "language_usage": {
            category: {
                "count": counts.get(category, 0),
                "percentage": percentages.get(category, 0.0)
            }
            for category in language_categories
        },

        "aggregate_usage": {
            "english_messages": english_messages,
            "english_percentage": percentage(
                english_messages
            ),

            "tanglish_messages": tanglish_messages,
            "tanglish_percentage": percentage(
                tanglish_messages
            ),

            "tamil_script_messages": tamil_script_messages,
            "tamil_script_percentage": percentage(
                tamil_script_messages
            ),

            "mixed_language_messages": mixed_messages,
            "mixed_language_percentage": percentage(
                mixed_messages
            )
        }
    }


# ============================================================
# COMPARISON BETWEEN SPEAKERS
# ============================================================

speaker_names = list(output_profiles.keys())

comparison = {}

if len(speaker_names) >= 2:

    speaker_a = speaker_names[0]
    speaker_b = speaker_names[1]

    profile_a = output_profiles[speaker_a]
    profile_b = output_profiles[speaker_b]

    comparison = {
        "speaker_a": speaker_a,
        "speaker_b": speaker_b,
        "differences": {}
    }

    for category in language_categories:

        a_percentage = profile_a[
            "language_usage"
        ][category]["percentage"]

        b_percentage = profile_b[
            "language_usage"
        ][category]["percentage"]

        comparison["differences"][category] = {
            speaker_a: a_percentage,
            speaker_b: b_percentage,
            "absolute_difference": round(
                abs(a_percentage - b_percentage),
                2
            )
        }


# ============================================================
# SAVE
# ============================================================

output = {
    "analysis": "Speaker Language Profile",

    "description": (
        "Aggregated language-use characteristics for each "
        "speaker based on message-level language classification."
    ),

    "speakers": output_profiles,

    "comparison": comparison
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

print("\n========== SPEAKER LANGUAGE PROFILE ==========\n")

for speaker, profile in output_profiles.items():

    print(f"\n--- {speaker} ---")

    print(
        f"Dominant message language: "
        f"{profile['dominant_message_language']}"
    )

    print(
        f"English: "
        f"{profile['aggregate_usage']['english_percentage']}%"
    )

    print(
        f"Tanglish: "
        f"{profile['aggregate_usage']['tanglish_percentage']}%"
    )

    print(
        f"Tamil script: "
        f"{profile['aggregate_usage']['tamil_script_percentage']}%"
    )

    print(
        f"Mixed language: "
        f"{profile['aggregate_usage']['mixed_language_percentage']}%"
    )

print("\nSaved:")
print(OUTPUT_FILE)