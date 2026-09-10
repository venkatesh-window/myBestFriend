import json
from pathlib import Path

BASE = Path("data/processed")

FILES = {
    "basic_stats": BASE / "basic_stats.json",
    "message_length": BASE / "message_length.json",
    "emoji_analysis": BASE / "emoji_analysis.json",
    "word_analysis": BASE / "word_analysis.json",
    "timing_analysis": BASE / "timing_analysis.json",
    "response_gaps": BASE / "response_gaps.json",
    "tanglish_analysis": BASE / "tanglish_analysis.json",
    "conversation_sessions": BASE / "conversation_sessions.json",
}


def load_json(path):
    if not path.exists():
        print(f"⚠️ Missing: {path}")
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


profile = {}

for name, path in FILES.items():
    data = load_json(path)

    if data is not None:
        profile[name] = data


OUTPUT_FILE = BASE / "conversation_analysis_profile.json"

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(
        profile,
        file,
        ensure_ascii=False,
        indent=2
    )


print("\n========== ANALYSIS PROFILE ==========\n")

print("Included analyses:")

for name in profile:
    print(f"✓ {name}")

print(f"\nSaved to:")
print(OUTPUT_FILE)