import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict


# ==========================================
# 1. LOAD DATA
# ==========================================

INPUT_FILE = Path("data/processed/messages.json")

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)

print("✅ messages.json loaded")


# ==========================================
# 2. PARSE TIMESTAMPS
# ==========================================

def parse_timestamp(timestamp):

    return datetime.strptime(
        timestamp,
        "%d/%m/%y, %H:%M"
    )


# ==========================================
# 3. STORAGE
# ==========================================

messages_by_hour = Counter()
messages_by_date = Counter()

response_times = defaultdict(list)

largest_gaps = []

previous_message = None


# ==========================================
# 4. ANALYZE
# ==========================================

for message in messages:

    timestamp = message.get("timestamp")
    sender = message.get("sender")

    if not timestamp:
        continue

    current_time = parse_timestamp(timestamp)


    # --------------------------------------
    # MESSAGE BY HOUR
    # --------------------------------------

    messages_by_hour[current_time.hour] += 1


    # --------------------------------------
    # MESSAGE BY DATE
    # --------------------------------------

    date = current_time.date()

    messages_by_date[str(date)] += 1


    # --------------------------------------
    # RESPONSE GAP
    # --------------------------------------

    if previous_message is not None:

        previous_time = parse_timestamp(
            previous_message["timestamp"]
        )

        previous_sender = previous_message.get("sender")

        gap_seconds = (
            current_time - previous_time
        ).total_seconds()


        # Only count when the sender changes.
        if (
            sender
            and previous_sender
            and sender != previous_sender
            and gap_seconds >= 0
        ):

            response_times[sender].append(
                gap_seconds
            )

            largest_gaps.append({
                "gap_seconds": gap_seconds,
                "sender": sender,
                "previous_sender": previous_sender,
                "timestamp": timestamp
            })


    previous_message = message


# ==========================================
# 5. FORMAT TIME
# ==========================================

def format_duration(seconds):

    if seconds < 60:
        return f"{seconds:.0f} seconds"

    minutes = seconds / 60

    if minutes < 60:
        return f"{minutes:.1f} minutes"

    hours = minutes / 60

    if hours < 24:
        return f"{hours:.1f} hours"

    days = hours / 24

    return f"{days:.1f} days"


# ==========================================
# 6. REPORT — HOURLY
# ==========================================

print()
print("=" * 65)
print("                 MESSAGES BY HOUR")
print("=" * 65)

for hour in range(24):

    count = messages_by_hour[hour]

    print(f"{hour:02d}:00 - {count}")


# ==========================================
# 7. REPORT — RESPONSE TIMES
# ==========================================

print()
print("=" * 65)
print("                 RESPONSE TIME")
print("=" * 65)


for sender, times in response_times.items():

    if not times:
        continue

    average = sum(times) / len(times)

    fastest = min(times)
    slowest = max(times)

    print()
    print(f"SENDER: {sender}")
    print("-" * 40)

    print(
        f"Responses analyzed : {len(times)}"
    )

    print(
        f"Average response   : "
        f"{format_duration(average)}"
    )

    print(
        f"Fastest response   : "
        f"{format_duration(fastest)}"
    )

    print(
        f"Longest response   : "
        f"{format_duration(slowest)}"
    )


# ==========================================
# 8. LONGEST GAPS
# ==========================================

largest_gaps.sort(
    key=lambda x: x["gap_seconds"],
    reverse=True
)


print()
print("=" * 65)
print("                 LONGEST RESPONSE GAPS")
print("=" * 65)

for gap in largest_gaps[:20]:

    print()
    print(
        f"Gap: "
        f"{format_duration(gap['gap_seconds'])}"
    )

    print(
        f"{gap['previous_sender']} → "
        f"{gap['sender']}"
    )

    print(
        f"At: {gap['timestamp']}"
    )


# ==========================================
# 9. MOST ACTIVE DAYS
# ==========================================

print()
print("=" * 65)
print("                 MOST ACTIVE DAYS")
print("=" * 65)

for date, count in messages_by_date.most_common(20):

    print(f"{date}: {count} messages")


print()
print("=" * 65)
print("✅ TIMING ANALYSIS COMPLETED")
print("=" * 65)
# ==========================================
# 10. SAVE ANALYSIS RESULTS
# ==========================================

OUTPUT_FILE = Path("data/processed/timing_analysis.json")

timing_results = {
    "messages_by_hour": {
        str(hour): count
        for hour, count in sorted(messages_by_hour.items())
    },

    "messages_by_date": dict(messages_by_date),

    "response_times": {
        sender: {
            "responses_analyzed": len(times),
            "average_seconds": (
                sum(times) / len(times)
                if times
                else 0
            ),
            "fastest_seconds": (
                min(times)
                if times
                else 0
            ),
            "longest_seconds": (
                max(times)
                if times
                else 0
            )
        }
        for sender, times in response_times.items()
    },

    "longest_gaps": largest_gaps[:20],

    "most_active_days": [
        {
            "date": date,
            "message_count": count
        }
        for date, count in messages_by_date.most_common(20)
    ]
}


with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        timing_results,
        file,
        ensure_ascii=False,
        indent=2
    )


print(f"\nSaved to: {OUTPUT_FILE}")