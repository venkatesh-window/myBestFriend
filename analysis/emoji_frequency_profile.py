import json
from collections import Counter
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "data/processed/compound_emoji_analysis.json"
)

OUTPUT_FILE = Path(
    "data/processed/emoji_frequency_profile.json"
)


# ============================================================
# LOAD DATA
# ============================================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


# ============================================================
# ANALYSIS
# ============================================================

output = {
    "analysis": "emoji_frequency_profile",
    "description": (
        "Speaker-specific emoji frequency, ranking, "
        "share, and concentration profile."
    ),
    "speakers": {}
}


for speaker, speaker_data in data["speakers"].items():

    total_emojis = speaker_data["total_emoji_sequences"]

    emoji_items = speaker_data["top_30_emoji_sequences"]

    # --------------------------------------------------------
    # Frequency ranking
    # --------------------------------------------------------

    frequency_profile = []

    for rank, item in enumerate(
        emoji_items,
        start=1
    ):

        emoji = item["emoji"]
        count = item["count"]

        percentage = (
            count / total_emojis * 100
            if total_emojis
            else 0
        )

        frequency_profile.append({
            "rank": rank,
            "emoji": emoji,
            "count": count,
            "percentage_of_all_emojis": round(
                percentage,
                2
            )
        })

    # --------------------------------------------------------
    # Top emoji concentration
    # --------------------------------------------------------

    top_1_count = (
        emoji_items[0]["count"]
        if len(emoji_items) >= 1
        else 0
    )

    top_5_count = sum(
        item["count"]
        for item in emoji_items[:5]
    )

    top_10_count = sum(
        item["count"]
        for item in emoji_items[:10]
    )

    top_1_percentage = (
        top_1_count / total_emojis * 100
        if total_emojis
        else 0
    )

    top_5_percentage = (
        top_5_count / total_emojis * 100
        if total_emojis
        else 0
    )

    top_10_percentage = (
        top_10_count / total_emojis * 100
        if total_emojis
        else 0
    )

    # --------------------------------------------------------
    # Unique emoji ratio
    # --------------------------------------------------------

    unique_emojis = speaker_data[
        "unique_emoji_sequences"
    ]

    unique_ratio = (
        unique_emojis / total_emojis
        if total_emojis
        else 0
    )

    # --------------------------------------------------------
    # Store
    # --------------------------------------------------------

    output["speakers"][speaker] = {

        "messages_analyzed":
            speaker_data["messages_analyzed"],

        "messages_with_emoji":
            speaker_data["messages_with_emoji"],

        "total_emoji_sequences":
            total_emojis,

        "unique_emoji_sequences":
            unique_emojis,

        "emoji_diversity_ratio":
            round(unique_ratio, 4),

        "top_1_concentration_percentage":
            round(top_1_percentage, 2),

        "top_5_concentration_percentage":
            round(top_5_percentage, 2),

        "top_10_concentration_percentage":
            round(top_10_percentage, 2),

        "frequency_profile":
            frequency_profile
    }


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

print("\n========== EMOJI FREQUENCY PROFILE ==========\n")

for speaker, profile in output["speakers"].items():

    print(f"Speaker: {speaker}")

    print(
        f"Total emojis: "
        f"{profile['total_emoji_sequences']}"
    )

    print(
        f"Unique emojis: "
        f"{profile['unique_emoji_sequences']}"
    )

    print(
        f"Emoji diversity ratio: "
        f"{profile['emoji_diversity_ratio']}"
    )

    print(
        f"Top 1 concentration: "
        f"{profile['top_1_concentration_percentage']}%"
    )

    print(
        f"Top 5 concentration: "
        f"{profile['top_5_concentration_percentage']}%"
    )

    print(
        f"Top 10 concentration: "
        f"{profile['top_10_concentration_percentage']}%"
    )

    print("\nTop emojis:")

    for item in profile["frequency_profile"][:15]:

        print(
            f"  {item['rank']:>2}. "
            f"{item['emoji']} "
            f"→ {item['count']} "
            f"({item['percentage_of_all_emojis']}%)"
        )

    print(
        "\n--------------------------------------------"
    )


print(
    f"\nSaved to: {OUTPUT_FILE}"
)