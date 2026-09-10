import re
import json
from pathlib import Path
from collections import Counter


# ==========================================
# 1. FILE PATHS
# ==========================================

INPUT_FILE = Path("data/raw/whatsapp/chat.txt")
MEDIA_FOLDER = Path("data/raw/whatsapp/media")
OUTPUT_FILE = Path("data/processed/messages.json")


# ==========================================
# 2. CHECK FILES
# ==========================================

if not INPUT_FILE.exists():
    print("❌ chat.txt not found!")
    print(f"Expected: {INPUT_FILE}")
    exit()

if not MEDIA_FOLDER.exists():
    print("⚠️ Media folder not found!")
    print(f"Expected: {MEDIA_FOLDER}")
    print("Text parsing will continue, but media cannot be verified.")


# Create processed folder
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# ==========================================
# 3. READ CHAT
# ==========================================

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    lines = file.readlines()

print("✅ WhatsApp chat loaded!")
print(f"Raw lines: {len(lines)}")


# ==========================================
# 4. WHATSAPP MESSAGE PATTERN
# ==========================================

message_pattern = re.compile(
    r"^(\d{2}/\d{2}/\d{2}),\s(\d{2}:\d{2})\s-\s(.*)$"
)


# ==========================================
# 5. MEDIA TYPES
# ==========================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif"
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv"
}

AUDIO_EXTENSIONS = {
    ".opus",
    ".mp3",
    ".m4a",
    ".wav",
    ".aac"
}

DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".txt"
}


# ==========================================
# 6. DETECT MEDIA TYPE
# ==========================================

def get_media_type(filename):

    extension = Path(filename).suffix.lower()

    if extension in IMAGE_EXTENSIONS:
        return "image"

    if extension in VIDEO_EXTENSIONS:
        return "video"

    if extension in AUDIO_EXTENSIONS:
        return "audio"

    if extension in DOCUMENT_EXTENSIONS:
        return "document"

    return "other"


# ==========================================
# 7. FIND MEDIA FILENAME
# ==========================================

def detect_media(message):

    if "(file attached)" not in message.lower():
        return None

    # Get everything before "(file attached)"
    filename = message.split("(file attached)", 1)[0].strip()

    if not filename:
        return None

    return filename


# ==========================================
# 8. PARSE CHAT
# ==========================================

messages = []

current_message = None

multiline_count = 0


for line in lines:

    line = line.rstrip("\n")

    match = message_pattern.match(line)

    # ======================================
    # NEW MESSAGE
    # ======================================

    if match:

        # Save previous message
        if current_message is not None:
            messages.append(current_message)

        date = match.group(1)
        time = match.group(2)
        message_part = match.group(3)

        timestamp = f"{date}, {time}"

        # ==================================
        # FIND SENDER
        # ==================================

        if ": " in message_part:

            sender, message_text = message_part.split(": ", 1)

        else:

            sender = None
            message_text = message_part


        # ==================================
        # CHECK DELETED MESSAGE
        # ==================================

        is_deleted = (
            "this message was deleted" in message_text.lower()
        )


        # ==================================
        # CHECK MEDIA
        # ==================================

        media_filename = detect_media(message_text)

        is_media = media_filename is not None


        if is_media:

            media_type = get_media_type(media_filename)

            media_path = MEDIA_FOLDER / media_filename

            media_exists = media_path.exists()

        else:

            media_type = None
            media_path = None
            media_exists = False


        # ==================================
        # CREATE MESSAGE
        # ==================================

        current_message = {

            "id": len(messages) + 1,

            "timestamp": timestamp,

            "sender": sender,

            "message": message_text,

            "is_media": is_media,

            "media_filename": media_filename,

            "media_type": media_type,

            "media_path": (
                str(media_path)
                if is_media
                else None
            ),

            "media_exists": media_exists,

            "is_deleted": is_deleted
        }


    # ======================================
    # CONTINUATION LINE
    # ======================================

    else:

        if current_message is not None:

            if line.strip():

                current_message["message"] += "\n" + line

                multiline_count += 1


# ==========================================
# 9. SAVE FINAL MESSAGE
# ==========================================

if current_message is not None:
    messages.append(current_message)


# ==========================================
# 10. FIX MESSAGE IDs
# ==========================================

for index, message in enumerate(messages, start=1):
    message["id"] = index


# ==========================================
# 11. SAVE JSON
# ==========================================

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        messages,
        file,
        ensure_ascii=False,
        indent=2
    )


# ==========================================
# 12. STATISTICS
# ==========================================

sender_counts = Counter()

media_count = 0
deleted_count = 0
media_found = 0
media_missing = 0


for message in messages:

    sender = message["sender"]

    if sender:
        sender_counts[sender] += 1

    if message["is_media"]:

        media_count += 1

        if message["media_exists"]:
            media_found += 1
        else:
            media_missing += 1

    if message["is_deleted"]:
        deleted_count += 1


# ==========================================
# 13. REPORT
# ==========================================

print()
print("=" * 50)
print("             PARSER REPORT")
print("=" * 50)

print(f"Total raw lines       : {len(lines)}")
print(f"Total messages        : {len(messages)}")
print(f"Multiline lines       : {multiline_count}")

print()
print("MESSAGES PER PERSON")
print("-" * 30)

for person, count in sender_counts.most_common():

    print(f"{person}: {count}")


print()
print("MEDIA")
print("-" * 30)

print(f"Media messages        : {media_count}")
print(f"Media files found     : {media_found}")
print(f"Media files missing   : {media_missing}")

print()
print("DELETED")
print("-" * 30)

print(f"Deleted messages      : {deleted_count}")


print()
print("=" * 50)
print("✅ PARSING COMPLETED")
print("=" * 50)

print(f"Output: {OUTPUT_FILE}")