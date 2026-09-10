import json
from collections import Counter
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path("data/processed/messages.json")

OUTPUT_FILE = Path(
    "data/processed/emoji_preference_profile.json"
)


# ============================================================
# EMOJI DETECTION
# ============================================================

def is_emoji_base(char):
    code = ord(char)

    return (
        0x1F300 <= code <= 0x1FAFF
        or 0x2600 <= code <= 0x27BF
        or 0x2300 <= code <= 0x23FF
        or 0x2B00 <= code <= 0x2BFF
    )


def is_skin_tone(char):
    return 0x1F3FB <= ord(char) <= 0x1F3FF


def is_variation_selector(char):
    return char == "\uFE0F"


def is_zwj(char):
    return char == "\u200D"


def is_regional_indicator(char):
    return 0x1F1E6 <= ord(char) <= 0x1F1FF


# ============================================================
# EXTRACT EMOJI SEQUENCES
# ============================================================

def extract_emojis(text):

    emojis = []
    i = 0

    while i < len(text):

        char = text[i]

        # ----------------------------------------------------
        # Keycaps
        # ----------------------------------------------------

        if char.isdigit() or char in "#*":

            if i + 1 < len(text):

                j = i + 1

                if text[j] == "\uFE0F":
                    j += 1

                if (
                    j < len(text)
                    and text[j] == "\u20E3"
                ):

                    emojis.append(
                        text[i:j + 1]
                    )

                    i = j + 1
                    continue

        # ----------------------------------------------------
        # Flags
        # ----------------------------------------------------

        if is_regional_indicator(char):

            if (
                i + 1 < len(text)
                and is_regional_indicator(text[i + 1])
            ):

                emojis.append(
                    text[i:i + 2]
                )

                i += 2
                continue

        # ----------------------------------------------------
        # Normal / compound emoji
        # ----------------------------------------------------

        if is_emoji_base(char):

            sequence = char
            i += 1

            # Skin tone
            if (
                i < len(text)
                and is_skin_tone(text[i])
            ):
                sequence += text[i]
                i += 1

            # Variation selector
            if (
                i < len(text)
                and is_variation_selector(text[i])
            ):
                sequence += text[i]
                i += 1

            # ZWJ sequence
            while (
                i < len(text)
                and is_zwj(text[i])
            ):

                sequence += text[i]
                i += 1

                if i >= len(text):
                    break

                if is_emoji_base(text[i]):
                    sequence += text[i]
                    i += 1

                if (
                    i < len(text)
                    and is_skin_tone(text[i])
                ):
                    sequence += text[i]
                    i += 1

                if (
                    i < len(text)
                    and is_variation_selector(text[i])
                ):
                    sequence += text[i]
                    i += 1

            emojis.append(sequence)

            continue

        i += 1

    return emojis


# ============================================================
# LOAD DATA
# ============================================================

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    messages = json.load(f)


# ============================================================
# COLLECT SPEAKER DATA
# ============================================================

speaker_data = {}


for item in messages:

    sender = item.get("sender")
    message = item.get("message")

    if not sender:
        continue

    if not message:
        continue

    if item.get("is_media"):
        continue

    if item.get("is_deleted"):
        continue

    if sender not in speaker_data:

        speaker_data[sender] = {
            "messages": 0,
            "messages_with_emoji": 0,
            "total_emojis": 0,
            "emoji_counter": Counter()
        }

    speaker_data[sender]["messages"] += 1

    emojis = extract_emojis(message)

    if emojis:

        speaker_data[sender][
            "messages_with_emoji"
        ] += 1

        speaker_data[sender][
            "total_emojis"
        ] += len(emojis)

        speaker_data[sender][
            "emoji_counter"
        ].update(emojis)


# ============================================================
# GLOBAL EMOJI COUNTS
# ============================================================

global_counter = Counter()

for data in speaker_data.values():

    global_counter.update(
        data["emoji_counter"]
    )


# ============================================================
# BUILD PROFILE
# ============================================================

output = {
    "analysis": "emoji_preference_profile",
    "description": (
        "Speaker-specific emoji usage rate, "
        "preference, dominance, and distinctiveness."
    ),
    "speakers": {}
}


for speaker, data in speaker_data.items():

    total_messages = data["messages"]
    emoji_messages = data["messages_with_emoji"]
    total_emojis = data["total_emojis"]
    counter = data["emoji_counter"]

    # --------------------------------------------------------
    # Basic rates
    # --------------------------------------------------------

    emoji_message_rate = (
        emoji_messages / total_messages * 100
        if total_messages
        else 0
    )

    emojis_per_message = (
        total_emojis / total_messages
        if total_messages
        else 0
    )

    emojis_per_emoji_message = (
        total_emojis / emoji_messages
        if emoji_messages
        else 0
    )

    # --------------------------------------------------------
    # Preference profile
    # --------------------------------------------------------

    preferences = []

    for emoji, count in counter.most_common():

        percentage = (
            count / total_emojis * 100
            if total_emojis
            else 0
        )

        global_count = global_counter[emoji]

        speaker_share = (
            count / global_count * 100
            if global_count
            else 0
        )

        preferences.append({
            "emoji": emoji,
            "count": count,
            "percentage_of_speaker_emojis": round(
                percentage,
                2
            ),
            "share_of_all_speaker_usage": round(
                speaker_share,
                2
            )
        })

    # --------------------------------------------------------
    # Concentration
    # --------------------------------------------------------

    top_3_count = sum(
        count
        for _, count in counter.most_common(3)
    )

    top_5_count = sum(
        count
        for _, count in counter.most_common(5)
    )

    top_10_count = sum(
        count
        for _, count in counter.most_common(10)
    )

    top_3_percentage = (
        top_3_count / total_emojis * 100
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
    # Store
    # --------------------------------------------------------

    output["speakers"][speaker] = {

        "messages_analyzed":
            total_messages,

        "messages_with_emoji":
            emoji_messages,

        "emoji_message_rate_percentage":
            round(
                emoji_message_rate,
                2
            ),

        "total_emojis":
            total_emojis,

        "unique_emojis":
            len(counter),

        "emojis_per_message":
            round(
                emojis_per_message,
                3
            ),

        "emojis_per_emoji_message":
            round(
                emojis_per_emoji_message,
                3
            ),

        "top_3_concentration_percentage":
            round(
                top_3_percentage,
                2
            ),

        "top_5_concentration_percentage":
            round(
                top_5_percentage,
                2
            ),

        "top_10_concentration_percentage":
            round(
                top_10_percentage,
                2
            ),

        "emoji_preferences":
            preferences[:50]
    }


# ============================================================
# COMPARE SPEAKERS
# ============================================================

speaker_names = list(speaker_data.keys())

if len(speaker_names) >= 2:

    speaker_a = speaker_names[0]
    speaker_b = speaker_names[1]

    counter_a = speaker_data[
        speaker_a
    ]["emoji_counter"]

    counter_b = speaker_data[
        speaker_b
    ]["emoji_counter"]

    all_emojis = (
        set(counter_a)
        | set(counter_b)
    )

    distinctive = {
        speaker_a: [],
        speaker_b: []
    }

    for emoji in all_emojis:

        count_a = counter_a[emoji]
        count_b = counter_b[emoji]

        if count_a == 0 and count_b == 0:
            continue

        # ----------------------------------------------------
        # Normalized frequency
        # ----------------------------------------------------

        total_a = sum(counter_a.values())
        total_b = sum(counter_b.values())

        freq_a = (
            count_a / total_a
            if total_a
            else 0
        )

        freq_b = (
            count_b / total_b
            if total_b
            else 0
        )

        # ----------------------------------------------------
        # Distinctiveness ratio
        # ----------------------------------------------------

        ratio_a = (
            (freq_a + 1e-9)
            / (freq_b + 1e-9)
        )

        ratio_b = (
            (freq_b + 1e-9)
            / (freq_a + 1e-9)
        )

        if count_a >= 3 and ratio_a > 2:

            distinctive[speaker_a].append({
                "emoji": emoji,
                "count": count_a,
                "other_speaker_count": count_b,
                "distinctiveness_ratio": round(
                    ratio_a,
                    2
                )
            })

        if count_b >= 3 and ratio_b > 2:

            distinctive[speaker_b].append({
                "emoji": emoji,
                "count": count_b,
                "other_speaker_count": count_a,
                "distinctiveness_ratio": round(
                    ratio_b,
                    2
                )
            })

    distinctive[speaker_a].sort(
        key=lambda x: x["distinctiveness_ratio"],
        reverse=True
    )

    distinctive[speaker_b].sort(
        key=lambda x: x["distinctiveness_ratio"],
        reverse=True
    )

    output["speaker_comparison"] = {
        "speakers": [
            speaker_a,
            speaker_b
        ],
        "distinctive_emojis": {
            speaker_a:
                distinctive[speaker_a][:30],

            speaker_b:
                distinctive[speaker_b][:30]
        }
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

print(
    "\n========== EMOJI PREFERENCE PROFILE ==========\n"
)

for speaker, profile in output["speakers"].items():

    print(f"Speaker: {speaker}")

    print(
        f"Emoji message rate: "
        f"{profile['emoji_message_rate_percentage']}%"
    )

    print(
        f"Total emojis: "
        f"{profile['total_emojis']}"
    )

    print(
        f"Unique emojis: "
        f"{profile['unique_emojis']}"
    )

    print(
        f"Emojis/message: "
        f"{profile['emojis_per_message']}"
    )

    print(
        f"Emojis/emoji-message: "
        f"{profile['emojis_per_emoji_message']}"
    )

    print(
        f"Top 5 concentration: "
        f"{profile['top_5_concentration_percentage']}%"
    )

    print("\nTop preferences:")

    for item in profile[
        "emoji_preferences"
    ][:15]:

        print(
            f"  {item['emoji']} → "
            f"{item['count']} "
            f"({item['percentage_of_speaker_emojis']}%)"
        )

    print(
        "\n---------------------------------------------"
    )


# ============================================================
# DISTINCTIVE EMOJIS
# ============================================================

if "speaker_comparison" in output:

    print(
        "\n========== DISTINCTIVE EMOJIS ==========\n"
    )

    for speaker, emojis in (
        output[
            "speaker_comparison"
        ]["distinctive_emojis"].items()
    ):

        print(f"{speaker}:")

        for item in emojis[:15]:

            print(
                f"  {item['emoji']} → "
                f"{item['count']} uses | "
                f"ratio {item['distinctiveness_ratio']}x"
            )

        print()


print(
    f"Saved to: {OUTPUT_FILE}"
)