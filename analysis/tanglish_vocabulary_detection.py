import json
import re
from collections import Counter
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "data/processed/messages.json"
)

OUTPUT_FILE = Path(
    "data/processed/tanglish_vocabulary_detection.json"
)


# ============================================================
# TANGlish VOCABULARY
# ============================================================
# Practical starter vocabulary.
# This is NOT intended to be a complete Tamil dictionary.
# It will be expanded later using the actual conversation data.

TANGLISH_WORDS = {
    # Pronouns
    "naan", "na", "nanu",
    "nee", "ne", "neenga",
    "unga", "ungal",
    "en", "ennoda",
    "un", "unnoda",
    "avan", "ava", "avanga",
    "athu", "idhu", "ithu",

    # Question words
    "enna", "ennaku", "enaku",
    "epdi", "eppadi",
    "enga", "engae",
    "engay", "engada",
    "yenga",
    "eppo", "eppo",
    "yen", "yaen",
    "ethuku", "edhuku",
    "yaaru", "yaru",
    "evlo", "evalo",
    "ennaiku", "eppa",

    # Common verbs
    "pannu", "pannunga",
    "panra", "pandra",
    "pannitu", "pannita",
    "panniten", "pannitaen",
    "pannuva", "pannuven",
    "pannala",
    "pannadha",

    "sollu", "solra",
    "sonna", "sonnen",
    "sollunga",

    "va", "vaa", "varen",
    "varra", "varum",
    "vandha", "vandhen",
    "vantha",

    "po", "pora", "poren",
    "pogum", "pona",
    "ponen",

    "iru", "iruka", "irukku",
    "iruken", "iruken",
    "irundha", "iruntha",
    "irukum",

    "sapdu", "saptiya",
    "sapten", "sapta",
    "sapdunga",

    "padichiya", "padichen",
    "padika", "padikuren",

    "paaka", "paatha",
    "paathen", "paakuren",

    # Common expressions
    "seri", "sari",
    "okay", "ok",
    "ama", "aama",
    "aamaa",
    "illa", "illai",
    "illaya",
    "venam", "vendam",
    "venum",
    "theva", "thevai",
    "romba",
    "konjam",
    "nalla",
    "super",
    "semma",
    "vera",
    "apdi", "ippadi",
    "inga", "anga",
    "ingaye", "angaye",
    "ippo", "ippa",
    "appo", "appa",

    # Social / conversational
    "da", "di",
    "machan", "macha",
    "bro",
    "anna", "akka",
    "thambi", "thangachi",
    "pa", "ma",

    # Feelings / reactions
    "santhosham",
    "kavalai",
    "kovam",
    "azhaga",
    "azhagu",
    "kashtam",
    "bayama",
    "bayam",

    # Common nouns
    "veedu",
    "veetla",
    "veliya",
    "velila",
    "ooru",
    "naal",
    "innaiku",
    "netru",
    "naalaiku",
    "kaalai",
    "iravu",
    "neram",

    # Connectors
    "aana",
    "ana",
    "apram",
    "appuram",
    "adhuku",
    "athuku",
    "adhana",
    "athana",
    "because",
    "but"
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_word(word):

    word = word.lower()

    # Remove surrounding apostrophes
    word = word.strip("'")

    return word


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):

    return re.findall(
        r"[a-zA-Z]+(?:'[a-zA-Z]+)?",
        text.lower()
    )


# ============================================================
# DETECT TANGLISH WORDS
# ============================================================

def detect_tanglish_words(text):

    words = tokenize(text)

    tanglish = []

    for word in words:

        normalized = normalize_word(word)

        if normalized in TANGLISH_WORDS:

            tanglish.append(normalized)

    return tanglish


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
# ANALYSIS
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
            "messages_analyzed": 0,
            "messages_with_tanglish": 0,
            "total_words": 0,
            "total_tanglish_words": 0,
            "tanglish_counter": Counter(),
            "examples": []
        }

    data = speaker_data[sender]

    data["messages_analyzed"] += 1

    words = tokenize(message)

    data["total_words"] += len(words)

    tanglish_words = detect_tanglish_words(
        message
    )

    if tanglish_words:

        data["messages_with_tanglish"] += 1

        data["total_tanglish_words"] += (
            len(tanglish_words)
        )

        data["tanglish_counter"].update(
            tanglish_words
        )

        # Keep examples
        if len(data["examples"]) < 15:

            data["examples"].append({
                "message": message,
                "tanglish_words": tanglish_words
            })


# ============================================================
# BUILD OUTPUT
# ============================================================

output = {
    "analysis": "tanglish_vocabulary_detection",
    "description": (
        "Detects common Romanized Tamil vocabulary "
        "inside English-script messages."
    ),
    "dictionary_size": len(TANGLISH_WORDS),
    "speakers": {}
}


for speaker, data in speaker_data.items():

    total_messages = data[
        "messages_analyzed"
    ]

    total_words = data[
        "total_words"
    ]

    tanglish_messages = data[
        "messages_with_tanglish"
    ]

    tanglish_words = data[
        "total_tanglish_words"
    ]

    message_percentage = (
        tanglish_messages
        / total_messages
        * 100
        if total_messages
        else 0
    )

    word_percentage = (
        tanglish_words
        / total_words
        * 100
        if total_words
        else 0
    )

    output["speakers"][speaker] = {

        "messages_analyzed":
            total_messages,

        "messages_with_tanglish":
            tanglish_messages,

        "tanglish_message_percentage":
            round(
                message_percentage,
                2
            ),

        "total_words":
            total_words,

        "total_tanglish_words":
            tanglish_words,

        "tanglish_word_percentage":
            round(
                word_percentage,
                2
            ),

        "unique_tanglish_words":
            len(
                data["tanglish_counter"]
            ),

        "top_tanglish_words": [
            {
                "word": word,
                "count": count
            }

            for word, count
            in data[
                "tanglish_counter"
            ].most_common(50)
        ],

        "examples":
            data["examples"]
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
    "\n========== TANGLISH VOCABULARY ==========\n"
)

for speaker, data in output[
    "speakers"
].items():

    print(f"Speaker: {speaker}")

    print(
        f"Messages analyzed: "
        f"{data['messages_analyzed']}"
    )

    print(
        f"Messages with Tanglish: "
        f"{data['messages_with_tanglish']}"
    )

    print(
        f"Tanglish message %: "
        f"{data['tanglish_message_percentage']}%"
    )

    print(
        f"Total Tanglish words: "
        f"{data['total_tanglish_words']}"
    )

    print(
        f"Tanglish word %: "
        f"{data['tanglish_word_percentage']}%"
    )

    print(
        f"Unique Tanglish words: "
        f"{data['unique_tanglish_words']}"
    )

    print("\nTop Tanglish words:")

    for item in data[
        "top_tanglish_words"
    ][:20]:

        print(
            f"  {item['word']} "
            f"→ {item['count']}"
        )

    print("\nExamples:")

    for example in data[
        "examples"
    ][:5]:

        print(
            f"  {example['message'][:120]}"
        )

        print(
            f"    detected: "
            f"{', '.join(example['tanglish_words'])}"
        )

    print(
        "\n-----------------------------------------"
    )


print(
    f"\nDictionary size: "
    f"{len(TANGLISH_WORDS)}"
)

print(
    f"Saved to: {OUTPUT_FILE}"
)