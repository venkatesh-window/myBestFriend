import json
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path("data/processed")

FILES = {
    "frequency": BASE_DIR / "emoji_frequency_profile.json",
    "combinations": BASE_DIR / "emoji_combinations.json",
    "position": BASE_DIR / "emoji_position_analysis.json",
    "preference": BASE_DIR / "emoji_preference_profile.json",
    "context": BASE_DIR / "emoji_context_analysis.json",
}

OUTPUT_FILE = BASE_DIR / "emoji_style_profile.json"


# ============================================================
# LOAD JSON
# ============================================================

def load_json(path):

    if not path.exists():
        print(f"WARNING: Missing file: {path}")
        return {}

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


data = {
    name: load_json(path)
    for name, path in FILES.items()
}


# ============================================================
# FIND SPEAKERS
# ============================================================

speaker_sets = []

for source in data.values():

    if "speakers" in source:
        speaker_sets.append(
            set(source["speakers"].keys())
        )

if not speaker_sets:

    print("No speaker data found.")
    raise SystemExit

speakers = sorted(
    set.union(*speaker_sets)
)


# ============================================================
# BUILD PROFILE
# ============================================================

output = {
    "analysis": "emoji_style_profile",
    "description": (
        "Aggregated emoji expression style profile "
        "combining frequency, combinations, position, "
        "preferences, and contextual usage."
    ),
    "speakers": {}
}


for speaker in speakers:

    frequency = data[
        "frequency"
    ].get("speakers", {}).get(
        speaker, {}
    )

    combinations = data[
        "combinations"
    ].get("speakers", {}).get(
        speaker, {}
    )

    position = data[
        "position"
    ].get("speakers", {}).get(
        speaker, {}
    )

    preference = data[
        "preference"
    ].get("speakers", {}).get(
        speaker, {}
    )

    context = data[
        "context"
    ].get("speakers", {}).get(
        speaker, {}
    )

    # --------------------------------------------------------
    # Basic usage
    # --------------------------------------------------------

    emoji_message_rate = preference.get(
        "emoji_message_rate_percentage",
        0
    )

    emojis_per_message = preference.get(
        "emojis_per_message",
        0
    )

    emojis_per_emoji_message = preference.get(
        "emojis_per_emoji_message",
        0
    )

    total_emojis = preference.get(
        "total_emojis",
        0
    )

    unique_emojis = preference.get(
        "unique_emojis",
        0
    )

    # --------------------------------------------------------
    # Position
    # --------------------------------------------------------

    position_profile = position.get(
        "position_profile",
        {}
    )

    # --------------------------------------------------------
    # Preferences
    # --------------------------------------------------------

    preferences = preference.get(
        "emoji_preferences",
        []
    )

    top_preferences = preferences[:10]

    # --------------------------------------------------------
    # Combinations
    # --------------------------------------------------------

    top_pairs = combinations.get(
        "top_30_emoji_pairs",
        []
    )[:10]

    top_triples = combinations.get(
        "top_30_emoji_triples",
        []
    )[:10]

    top_sequences = combinations.get(
        "top_30_full_emoji_sequences",
        []
    )[:10]

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    emoji_contexts = context.get(
        "emoji_contexts",
        {}
    )

    context_profile = []

    for emoji, emoji_data in list(
        emoji_contexts.items()
    )[:10]:

        context_profile.append({
            "emoji": emoji,
            "usage_count":
                emoji_data.get(
                    "usage_count",
                    0
                ),
            "top_context_words":
                emoji_data.get(
                    "top_context_words",
                    []
                )[:10]
        })

    # --------------------------------------------------------
    # Style indicators
    # --------------------------------------------------------

    style_indicators = []

    if emoji_message_rate >= 50:
        style_indicators.append(
            "frequent_emoji_user"
        )
    elif emoji_message_rate >= 20:
        style_indicators.append(
            "moderate_emoji_user"
        )
    else:
        style_indicators.append(
            "low_emoji_user"
        )

    if emojis_per_emoji_message >= 2:
        style_indicators.append(
            "multi_emoji_expression"
        )

    if position_profile:

        end_percentage = position_profile.get(
            "end",
            {}
        ).get(
            "percentage",
            0
        )

        only_percentage = position_profile.get(
            "only_emoji",
            {}
        ).get(
            "percentage",
            0
        )

        beginning_percentage = position_profile.get(
            "beginning",
            {}
        ).get(
            "percentage",
            0
        )

        if end_percentage >= 50:
            style_indicators.append(
                "emoji_often_at_message_end"
            )

        if only_percentage >= 10:
            style_indicators.append(
                "emoji_only_responses"
            )

        if beginning_percentage >= 20:
            style_indicators.append(
                "emoji_often_at_message_start"
            )

    # --------------------------------------------------------
    # Build speaker profile
    # --------------------------------------------------------

    output["speakers"][speaker] = {

        "usage": {
            "total_emojis":
                total_emojis,

            "unique_emojis":
                unique_emojis,

            "emoji_message_rate_percentage":
                emoji_message_rate,

            "emojis_per_message":
                emojis_per_message,

            "emojis_per_emoji_message":
                emojis_per_emoji_message
        },

        "frequency": {
            "top_1_concentration_percentage":
                frequency.get(
                    "top_1_concentration_percentage",
                    0
                ),

            "top_5_concentration_percentage":
                frequency.get(
                    "top_5_concentration_percentage",
                    0
                ),

            "top_10_concentration_percentage":
                frequency.get(
                    "top_10_concentration_percentage",
                    0
                )
        },

        "position": position_profile,

        "top_preferences":
            top_preferences,

        "top_combinations": {
            "pairs":
                top_pairs,

            "triples":
                top_triples,

            "full_sequences":
                top_sequences
        },

        "context":
            context_profile,

        "style_indicators":
            style_indicators
    }


# ============================================================
# SPEAKER COMPARISON
# ============================================================

if len(speakers) >= 2:

    comparison = {}

    for metric in [
        "emoji_message_rate_percentage",
        "emojis_per_message",
        "emojis_per_emoji_message",
        "unique_emojis",
        "total_emojis"
    ]:

        comparison[metric] = {}

        for speaker in speakers:

            comparison[metric][speaker] = (
                output["speakers"][speaker]
                ["usage"]
                .get(metric, 0)
            )

    output["comparison"] = comparison


# ============================================================
# VALIDATION CHECKS
# ============================================================

validation = {
    "checks": [],
    "warnings": [],
    "status": "PASS"
}


# Check 1 — Data exists
for speaker in speakers:

    profile = output[
        "speakers"
    ][speaker]

    if profile["usage"]["total_emojis"] == 0:

        validation["warnings"].append(
            f"{speaker}: no emoji usage detected."
        )


# Check 2 — Position percentages
for speaker in speakers:

    position_profile = output[
        "speakers"
    ][speaker]["position"]

    if position_profile:

        total_percentage = sum(
            value.get("percentage", 0)
            for value in position_profile.values()
        )

        # Small tolerance for rounding
        if not 99.0 <= total_percentage <= 101.0:

            validation["warnings"].append(
                f"{speaker}: emoji position percentages "
                f"sum to {round(total_percentage, 2)}%."
            )


# Check 3 — Top preference consistency
for speaker in speakers:

    profile = output[
        "speakers"
    ][speaker]

    preferences = profile[
        "top_preferences"
    ]

    if preferences:

        counts = [
            item["count"]
            for item in preferences
        ]

        if counts != sorted(
            counts,
            reverse=True
        ):

            validation["warnings"].append(
                f"{speaker}: emoji preference ranking "
                f"is not properly sorted."
            )


# Check 4 — Combination data
for speaker in speakers:

    combinations = output[
        "speakers"
    ][speaker]["top_combinations"]

    if not (
        combinations["pairs"]
        or combinations["triples"]
        or combinations["full_sequences"]
    ):

        validation["warnings"].append(
            f"{speaker}: no emoji combinations detected."
        )


# Final validation status
if validation["warnings"]:

    validation["status"] = "PASS_WITH_WARNINGS"


validation["checks"].append(
    "Speaker emoji usage profile generated"
)

validation["checks"].append(
    "Emoji frequency profile included"
)

validation["checks"].append(
    "Emoji position profile included"
)

validation["checks"].append(
    "Emoji combination profile included"
)

validation["checks"].append(
    "Emoji context profile included"
)

validation["checks"].append(
    "Speaker comparison generated where possible"
)

output["validation"] = validation


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
    "\n========== EMOJI STYLE PROFILE ==========\n"
)

for speaker, profile in output[
    "speakers"
].items():

    print(f"Speaker: {speaker}")

    usage = profile["usage"]

    print(
        f"  Emoji message rate: "
        f"{usage['emoji_message_rate_percentage']}%"
    )

    print(
        f"  Emojis/message: "
        f"{usage['emojis_per_message']}"
    )

    print(
        f"  Emojis/emoji-message: "
        f"{usage['emojis_per_emoji_message']}"
    )

    print(
        f"  Total emojis: "
        f"{usage['total_emojis']}"
    )

    print(
        f"  Unique emojis: "
        f"{usage['unique_emojis']}"
    )

    print("\n  Style indicators:")

    for indicator in profile[
        "style_indicators"
    ]:

        print(
            f"    ✓ {indicator}"
        )

    print("\n  Top preferences:")

    for item in profile[
        "top_preferences"
    ][:10]:

        print(
            f"    {item['emoji']} "
            f"→ {item['count']}"
        )

    print(
        "\n-----------------------------------------"
    )


print(
    "\n========== VALIDATION ==========\n"
)

print(
    f"Status: "
    f"{validation['status']}"
)

if validation["warnings"]:

    print("\nWarnings:")

    for warning in validation["warnings"]:

        print(
            f"  ⚠ {warning}"
        )

else:

    print(
        "✓ No validation warnings."
    )


print(
    f"\nSaved to: {OUTPUT_FILE}"
)