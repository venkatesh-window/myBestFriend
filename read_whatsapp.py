from pathlib import Path
from collections import Counter


# --------------------------------------------------
# 1. WhatsApp TXT file
# --------------------------------------------------

file_path = Path("data/raw/WhatsApp/chat.txt")


# --------------------------------------------------
# 2. Check if file exists
# --------------------------------------------------

if not file_path.exists():
    print("❌ WhatsApp file not found!")
    print(f"Expected location: {file_path}")
    exit()


# --------------------------------------------------
# 3. Read the file
# --------------------------------------------------

with open(file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()


print("✅ WhatsApp file loaded!")
print(f"Total lines: {len(lines)}")


# --------------------------------------------------
# 4. Extract messages
# --------------------------------------------------

messages = []

for line in lines:

    line = line.strip()

    # Ignore empty lines
    if not line:
        continue

    # WhatsApp message lines contain " - "
    if " - " not in line:
        continue

    # Separate timestamp and message
    timestamp, message_part = line.split(" - ", 1)

    # Separate sender and message
    if ": " in message_part:

        sender, message = message_part.split(": ", 1)

        messages.append({
            "timestamp": timestamp,
            "sender": sender,
            "message": message
        })


# --------------------------------------------------
# 5. Print messages
# --------------------------------------------------

print("\n========== MESSAGES ==========\n")

for message in messages[:20]:
    print(
        f"{message['timestamp']} | "
        f"{message['sender']} | "
        f"{message['message']}"
    )


# --------------------------------------------------
# 6. Total messages
# --------------------------------------------------

print("\n========== STATISTICS ==========\n")

print(f"Total messages: {len(messages)}")


# --------------------------------------------------
# 7. Count messages per person
# --------------------------------------------------

message_counts = Counter(
    message["sender"]
    for message in messages
)


print("\nMessages per person:")

for person, count in message_counts.items():
    print(f"{person}: {count}")