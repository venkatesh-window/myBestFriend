import json
from pathlib import Path


INPUT_FILE = Path("data/processed/messages.json")


with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)


empty_messages = [
    message
    for message in messages
    if message.get("message") is None
    or message.get("message").strip() == ""
]


print("=" * 60)
print("EMPTY MESSAGE INSPECTION")
print("=" * 60)

print(f"Total empty messages: {len(empty_messages)}")

print()


for message in empty_messages[:30]:

    print("-" * 60)

    print("ID:", message.get("id"))
    print("Timestamp:", message.get("timestamp"))
    print("Sender:", message.get("sender"))
    print("Message:", repr(message.get("message")))
    print("Is media:", message.get("is_media"))
    print("Media filename:", message.get("media_filename"))
    print("Media type:", message.get("media_type"))
    print("Media exists:", message.get("media_exists"))
    print("Deleted:", message.get("is_deleted"))