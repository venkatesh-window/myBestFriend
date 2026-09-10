import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

INPUT_FILE = Path("data/processed/messages.json")

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


def parse_timestamp(timestamp):
    return datetime.strptime(timestamp, "%d/%m/%y, %H:%M")


# Store valid messages with timestamps
valid_messages = []

for message in messages:
    if not message.get("timestamp"):
        continue

    if not message.get("sender"):
        continue

    valid_messages.append({
        "timestamp": parse_timestamp(message["timestamp"]),
        "sender": message["sender"],
        "message": message.get("message", "")
    })


# --------------------------------------------------
# Calculate response gaps
# --------------------------------------------------

response_gaps = []

for i in range(1, len(valid_messages)):

    previous = valid_messages[i - 1]
    current = valid_messages[i]

    # Only calculate when the sender changes
    if previous["sender"] == current["sender"]:
        continue

    gap_minutes = (
        current["timestamp"] - previous["timestamp"]
    ).total_seconds() / 60

    if gap_minutes < 0:
        continue

    response_gaps.append({
        "from": previous["sender"],
        "to": current["sender"],
        "gap_minutes": round(gap_minutes, 2)
    })


# --------------------------------------------------
# Group by response direction
# --------------------------------------------------

direction_stats = defaultdict(list)

for gap in response_gaps:
    key = f"{gap['from']} -> {gap['to']}"
    direction_stats[key].append(gap["gap_minutes"])


print("\n========== RESPONSE GAP ANALYSIS ==========\n")

for direction, gaps in direction_stats.items():

    average = sum(gaps) / len(gaps)
    fastest = min(gaps)
    slowest = max(gaps)

    print(direction)
    print(f"  Responses: {len(gaps)}")
    print(f"  Average gap: {average:.2f} minutes")
    print(f"  Fastest gap: {fastest:.2f} minutes")
    print(f"  Slowest gap: {slowest:.2f} minutes")
    print()


# --------------------------------------------------
# Overall statistics
# --------------------------------------------------

all_gaps = [gap["gap_minutes"] for gap in response_gaps]

if all_gaps:

    print("========== OVERALL ==========\n")

    print(f"Total response gaps: {len(all_gaps)}")
    print(f"Average response gap: {sum(all_gaps) / len(all_gaps):.2f} minutes")
    print(f"Fastest response: {min(all_gaps):.2f} minutes")
    print(f"Longest response gap: {max(all_gaps):.2f} minutes")


# --------------------------------------------------
# Save results
# --------------------------------------------------

OUTPUT_FILE = Path("data/processed/response_gaps.json")

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(
        response_gaps,
        file,
        ensure_ascii=False,
        indent=2
    )

print(f"\nSaved to: {OUTPUT_FILE}")