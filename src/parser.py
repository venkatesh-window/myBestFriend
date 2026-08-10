import re
import sys

def parse_message(line: str) -> dict | None:
    """
    Parses a single line of WhatsApp chat into its components.
    
    Expected format:
    DD/MM/YY, HH:MM - SENDER: MESSAGE
    
    Returns a dictionary with 'date', 'time', 'sender', and 'message'
    if it's a valid message line. Otherwise returns None.
    """
    pattern = r'^(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}) - (.*?): (.*)$'
    
    match = re.match(pattern, line)
    if match:
        return {
            "date": match.group(1),
            "time": match.group(2),
            "sender": match.group(3),
            "message": match.group(4)
        }
    
    return None

def parse_chat(lines: list[str]) -> list[dict]:
    """
    Parses multiple lines of WhatsApp chat, combining multi-line messages.
    """
    parsed_messages = []
    current_message = None

    for line in lines:
        # Strip newline characters from the end
        line = line.rstrip('\n')
        
        # Does the line start a new message or event? 
        # Check for the date pattern: DD/MM/YY, HH:MM - 
        if re.match(r'^\d{2}/\d{2}/\d{2}, \d{2}:\d{2} - ', line):
            # Save the previous message if we have one
            if current_message:
                parsed_messages.append(current_message)
            
            # Start a new message
            current_message = parse_message(line)
        else:
            # It does not start with a date, so it's a continuation of the previous message.
            if current_message:
                current_message["message"] += "\n" + line

    # Don't forget to append the very last message in the chat
    if current_message:
        parsed_messages.append(current_message)
        
    return parsed_messages

if __name__ == "__main__":
    # Ensure Windows console can print emojis without throwing a charmap error
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
        
    # Test cases with multi-line messages
    test_chat = [
        "28/01/26, 10:00 - Sandhiya - My Best Friend: First line",
        "Second line",
        "Third line",
        "28/01/26, 17:47 - Venkatesh GS: No, I will ask the organiser regarding that. 🥲 Sorry",
        "28/01/26, 17:48 - Messages and calls are end-to-end encrypted. No one outside of this chat...", # System message
        "28/01/26, 17:49 - Sandhiya - My Best Friend: Okay thank you!",
        "28/01/26, 17:50 - Venkatesh GS: <Media omitted>",
        "28/01/26, 17:51 - You deleted this message",
        "28/01/26, 17:52 - Sandhiya - My Best Friend: Wait, what did you delete?"
    ]
    
    results = parse_chat(test_chat)
    for msg in results:
        print(f"Message from {msg['sender']} at {msg['time']}:")
        print(f"{msg['message']}")
        print("-" * 30)
