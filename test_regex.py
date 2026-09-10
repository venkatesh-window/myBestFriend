import re

lines = [
    "09/01/26, 21:18 - Person: Hello",
    "This is a continuation",
    "and this is another line",
    "09/01/26, 21:20 - Person: How are you?",
    "I wanted to ask you something"
]

pattern = r"^\d{2}/\d{2}/\d{2}, \d{2}:\d{2}"

messages = []
current_message = None

for line in lines:

    line = line.strip()

    # Check whether this is a new message
    if re.match(pattern, line):

        # Save previous message
        if current_message:
            messages.append(current_message)

        # Create new message
        timestamp, message_part = line.split(" - ", 1)

        if ": " in message_part:
            sender, message = message_part.split(": ", 1)

            current_message = {
                "timestamp": timestamp,
                "sender": sender,
                "message": message
            }

    else:
        # This is a continuation of previous message
        if current_message:
            current_message["message"] += "\n" + line


# Save final message
if current_message:
    messages.append(current_message)


# Print results
for message in messages:
    print("----------")
    print("Timestamp:", message["timestamp"])
    print("Sender:", message["sender"])
    print("Message:", message["message"])