import json
import re
from pathlib import Path
from collections import Counter


# ==========================================
# 1. LOAD DATA
# ==========================================

INPUT_FILE = Path("data/processed/messages.json")

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


# ==========================================
# 2. STORAGE
# ==========================================

word_counts = Counter()
bigram_counts = Counter()
trigram_counts = Counter()

sender_word_counts = {}
sender_bigram_counts = {}
sender_trigram_counts = {}

sender_message_counts = Counter()


# ==========================================
# 3. TOKENIZE TEXT
# ==========================================

def tokenize(text):

    # Keep letters, numbers and apostrophes.
    # Unicode is supported, so Tamil characters are preserved.
    return re.findall(
        r"[^\W_]+(?:['’][^\W_]+)*",
        text.lower(),
        flags=re.UNICODE
    )


# ==========================================
# 4. ANALYZE EACH MESSAGE
# ==========================================

for message in messages:

    sender = message.get("sender")

    if not sender:
        continue

    text = message.get("message") or ""

    words = tokenize(text)

    sender_message_counts[sender] += 1


    # Create counters for sender if needed
    if sender not in sender_word_counts:

        sender_word_counts[sender] = Counter()
        sender_bigram_counts[sender] = Counter()
        sender_trigram_counts[sender] = Counter()


    # ======================================
    # WORDS
    # ======================================

    for word in words:

        word_counts[word] += 1
        sender_word_counts[sender][word] += 1


    # ======================================
    # 2-WORD PHRASES
    # ======================================

    for i in range(len(words) - 1):

        phrase = f"{words[i]} {words[i + 1]}"

        bigram_counts[phrase] += 1
        sender_bigram_counts[sender][phrase] += 1


    # ======================================
    # 3-WORD PHRASES
    # ======================================

    for i in range(len(words) - 2):

        phrase = (
            f"{words[i]} "
            f"{words[i + 1]} "
            f"{words[i + 2]}"
        )

        trigram_counts[phrase] += 1
        sender_trigram_counts[sender][phrase] += 1


# ==========================================
# 5. REPORT
# ==========================================

print("=" * 65)
print("                  WORD ANALYSIS")
print("=" * 65)


for sender in sender_message_counts:

    print()
    print("=" * 65)
    print(f"SENDER: {sender}")
    print("=" * 65)


    print()
    print("TOP 30 WORDS")
    print("-" * 30)

    for word, count in sender_word_counts[sender].most_common(30):

        print(f"{word:<25} {count}")


    print()
    print("TOP 20 TWO-WORD PHRASES")
    print("-" * 30)

    for phrase, count in sender_bigram_counts[sender].most_common(20):

        print(f"{phrase:<35} {count}")


    print()
    print("TOP 20 THREE-WORD PHRASES")
    print("-" * 30)

    for phrase, count in sender_trigram_counts[sender].most_common(20):

        print(f"{phrase:<45} {count}")


print()
print("=" * 65)
print("✅ WORD ANALYSIS COMPLETED")
print("=" * 65)
# ==========================================
# 6. SAVE ANALYSIS RESULTS
# ==========================================

OUTPUT_FILE = Path("data/processed/word_analysis.json")

word_results = {}

for sender in sender_message_counts:

    word_results[sender] = {
        "message_count": sender_message_counts[sender],

        "top_words": dict(
            sender_word_counts[sender].most_common(30)
        ),

        "top_bigrams": dict(
            sender_bigram_counts[sender].most_common(20)
        ),

        "top_trigrams": dict(
            sender_trigram_counts[sender].most_common(20)
        )
    }


with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        word_results,
        file,
        ensure_ascii=False,
        indent=2
    )


print(f"\nSaved to: {OUTPUT_FILE}")