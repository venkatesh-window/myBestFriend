import json
from pathlib import Path
from collections import Counter


# ==========================================
# 1. FILE
# ==========================================

INPUT_FILE = Path("data/processed/messages.json")


if not INPUT_FILE.exists():
    print("❌ messages.json not found!")
    exit()


# ==========================================
# 2. LOAD DATA
# ==========================================

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


print("✅ messages.json loaded!")
print(f"Total records: {len(messages)}")


# ==========================================
# 3. VALIDATION COUNTERS
# ==========================================

errors = []

empty_messages = []
missing_timestamps = []
missing_senders = []

media_messages = []
missing_media_files = []

deleted_messages = []

multiline_messages = []

ids = []


# ==========================================
# 4. CHECK EACH MESSAGE
# ==========================================

for message in messages:

    message_id = message.get("id")
    timestamp = message.get("timestamp")
    sender = message.get("sender")
    text = message.get("message")

    ids.append(message_id)

    # --------------------------------------
    # ID
    # --------------------------------------

    if message_id is None:
        errors.append("Message without ID")

    # --------------------------------------
    # TIMESTAMP
    # --------------------------------------

    if not timestamp:
        missing_timestamps.append(message_id)

    # --------------------------------------
    # MESSAGE
    # --------------------------------------

    if text is None or text.strip() == "":
        empty_messages.append(message_id)

    # --------------------------------------
    # SENDER
    # --------------------------------------

    if not sender:
        missing_senders.append(message_id)

    # --------------------------------------
    # MEDIA
    # --------------------------------------

    if message.get("is_media"):

        media_messages.append(message_id)

        if not message.get("media_exists"):
            missing_media_files.append(
                message.get("media_filename")
            )

    # --------------------------------------
    # DELETED
    # --------------------------------------

    if message.get("is_deleted"):
        deleted_messages.append(message_id)

    # --------------------------------------
    # MULTILINE
    # --------------------------------------

    if text and "\n" in text:
        multiline_messages.append(message_id)


# ==========================================
# 5. CHECK DUPLICATE IDs
# ==========================================

id_counts = Counter(ids)

duplicate_ids = [
    message_id
    for message_id, count in id_counts.items()
    if count > 1
]


# ==========================================
# 6. SENDER STATISTICS
# ==========================================

sender_counts = Counter(
    message.get("sender")
    for message in messages
    if message.get("sender")
)


# ==========================================
# 7. PRINT REPORT
# ==========================================

print()
print("=" * 55)
print("              DATA VALIDATION REPORT")
print("=" * 55)

print()
print("GENERAL")
print("-" * 30)

print(f"Total messages       : {len(messages)}")
print(f"Duplicate IDs        : {len(duplicate_ids)}")
print(f"Missing timestamps   : {len(missing_timestamps)}")
print(f"Empty messages       : {len(empty_messages)}")
print(f"Missing senders      : {len(missing_senders)}")

print()
print("MESSAGES")
print("-" * 30)

print(f"Multiline messages   : {len(multiline_messages)}")
print(f"Deleted messages     : {len(deleted_messages)}")

print()
print("MEDIA")
print("-" * 30)

print(f"Media messages       : {len(media_messages)}")
print(f"Missing media files  : {len(missing_media_files)}")

print()
print("SENDERS")
print("-" * 30)

for sender, count in sender_counts.most_common():
    print(f"{sender}: {count}")


# ==========================================
# 8. SHOW PROBLEMS
# ==========================================

print()
print("=" * 55)
print("              VALIDATION RESULT")
print("=" * 55)

total_problems = (
    len(errors)
    + len(duplicate_ids)
    + len(missing_timestamps)
    + len(empty_messages)
)


if total_problems == 0:

    print("✅ STRUCTURAL VALIDATION PASSED")

else:

    print("⚠️ PROBLEMS FOUND")
    print(f"Total structural problems: {total_problems}")


# ==========================================
# 9. MEDIA WARNING
# ==========================================

if missing_media_files:

    print()
    print("⚠️ Some media files are missing.")
    print("This is not necessarily a parser error.")
    print(f"Missing media references: {len(missing_media_files)}")


print()
print("=" * 55)