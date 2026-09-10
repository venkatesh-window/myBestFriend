import json
from collections import Counter, defaultdict
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "language_style_classification.json"
OUTPUT_FILE = PROCESSED_DIR / "language_switching_patterns.json"


# ============================================================
# CONFIG
# ============================================================

MAX_EXAMPLES = 10


# ============================================================
# LOAD DATA
# ============================================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

messages = data.get("messages", [])


# ============================================================
# CLASSIFICATION GROUPS
# ============================================================

def language_group(classification):
    """
    Convert detailed classification into a simpler
    language group for switching analysis.
    """

    if classification == "english":
        return "english"

    if classification == "tamil_script":
        return "tamil_script"

    if classification == "tanglish":
        return "tanglish"

    if classification == "mixed_english_tanglish":
        return "mixed_english_tanglish"

    if classification == "mixed_tamil_english":
        return "mixed_tamil_english"

    if classification == "mixed_tamil_tanglish":
        return "mixed_tamil_tanglish"

    if classification == "mixed_all":
        return "mixed_all"

    return "unknown"


# ============================================================
# SPEAKER DATA
# ============================================================

speaker_messages = defaultdict(list)

for item in messages:

    speaker = item.get("sender")

    if not speaker:
        continue

    speaker_messages[speaker].append(item)


# ============================================================
# ANALYZE SWITCHING
# ============================================================

speaker_results = {}


for speaker, items in speaker_messages.items():

    if not items:
        continue

    transitions = Counter()
    examples = defaultdict(list)

    previous_group = None
    previous_message = None

    total_switches = 0

    # --------------------------------------------------------
    # Walk through messages
    # --------------------------------------------------------

    for item in items:

        classification = item.get(
            "classification",
            "unknown"
        )

        current_group = language_group(
            classification
        )

        current_message = item.get(
            "message",
            ""
        )

        if (
            previous_group is not None
            and current_group != previous_group
            and current_group != "unknown"
            and previous_group != "unknown"
        ):

            transition = (
                f"{previous_group} -> {current_group}"
            )

            transitions[transition] += 1
            total_switches += 1

            if len(examples[transition]) < MAX_EXAMPLES:

                examples[transition].append({
                    "previous_message": previous_message,
                    "previous_language": previous_group,
                    "current_message": current_message,
                    "current_language": current_group
                })

        previous_group = current_group
        previous_message = current_message

    # --------------------------------------------------------
    # Message count
    # --------------------------------------------------------

    total_messages = len(items)

    # --------------------------------------------------------
    # Switching rate
    # --------------------------------------------------------

    if total_messages > 1:

        switching_rate = round(
            (
                total_switches
                / (total_messages - 1)
            ) * 100,
            2
        )

    else:

        switching_rate = 0.0

    # --------------------------------------------------------
    # Most common transition
    # --------------------------------------------------------

    most_common_transition = None

    if transitions:

        transition, count = (
            transitions.most_common(1)[0]
        )

        most_common_transition = {
            "transition": transition,
            "count": count
        }

    # --------------------------------------------------------
    # Save speaker result
    # --------------------------------------------------------

    speaker_results[speaker] = {

        "total_messages": total_messages,

        "total_language_switches": total_switches,

        "switching_rate_percent": switching_rate,

        "most_common_transition": (
            most_common_transition
        ),

        "transition_counts": dict(
            transitions
        ),

        "transition_examples": dict(
            examples
        )
    }


# ============================================================
# OVERALL TRANSITIONS
# ============================================================

overall_transitions = Counter()

for profile in speaker_results.values():

    overall_transitions.update(
        profile["transition_counts"]
    )


# ============================================================
# SWITCHING TYPES
# ============================================================

switching_types = {
    "english_to_tanglish": 0,
    "tanglish_to_english": 0,
    "english_to_tamil_script": 0,
    "tamil_script_to_english": 0,
    "tanglish_to_tamil_script": 0,
    "tamil_script_to_tanglish": 0,
    "mixed_language_transitions": 0
}


for transition, count in overall_transitions.items():

    if transition == "english -> tanglish":
        switching_types[
            "english_to_tanglish"
        ] += count

    elif transition == "tanglish -> english":
        switching_types[
            "tanglish_to_english"
        ] += count

    elif transition == "english -> tamil_script":
        switching_types[
            "english_to_tamil_script"
        ] += count

    elif transition == "tamil_script -> english":
        switching_types[
            "tamil_script_to_english"
        ] += count

    elif transition == "tanglish -> tamil_script":
        switching_types[
            "tanglish_to_tamil_script"
        ] += count

    elif transition == "tamil_script -> tanglish":
        switching_types[
            "tamil_script_to_tanglish"
        ] += count

    else:
        switching_types[
            "mixed_language_transitions"
        ] += count


# ============================================================
# SAVE
# ============================================================

output = {

    "analysis": "Language Switching Patterns",

    "description": (
        "Measures changes between English, Tanglish, "
        "Tamil script and mixed-language message styles."
    ),

    "speaker_profiles": speaker_results,

    "overall_transition_counts": dict(
        overall_transitions
    ),

    "switching_types": switching_types
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

print("\n========== LANGUAGE SWITCHING PATTERNS ==========\n")


for speaker, profile in speaker_results.items():

    print(f"\n--- {speaker} ---")

    print(
        f"Total messages: "
        f"{profile['total_messages']}"
    )

    print(
        f"Language switches: "
        f"{profile['total_language_switches']}"
    )

    print(
        f"Switching rate: "
        f"{profile['switching_rate_percent']}%"
    )

    if profile["most_common_transition"]:

        print(
            "Most common transition: "
            f"{profile['most_common_transition']['transition']} "
            f"("
            f"{profile['most_common_transition']['count']}"
            f")"
        )

    print("\nTop transitions:")

    for transition, count in sorted(
        profile["transition_counts"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:15]:

        print(
            f"  {transition:<35} "
            f"{count}"
        )


print("\n--- SWITCHING TYPES ---")

for name, count in switching_types.items():

    print(
        f"  {name:<35} "
        f"{count}"
    )


print("\nSaved:")
print(OUTPUT_FILE)