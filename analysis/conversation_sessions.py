import json
from pathlib import Path
from datetime import datetime


# ==========================================
# 1. FILES
# ==========================================

INPUT_FILE = Path("data/processed/messages.json")
OUTPUT_FILE = Path("data/processed/conversation_sessions.json")


# ==========================================
# 2. LOAD DATA
# ==========================================

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    messages = json.load(file)

print("✅ messages.json loaded")
print(f"Total messages: {len(messages)}")


# ==========================================
# 3. TIMESTAMP PARSER
# ==========================================

def parse_timestamp(timestamp):

    return datetime.strptime(
        timestamp,
        "%d/%m/%y, %H:%M"
    )


# ==========================================
# 4. SESSION SETTINGS
# ==========================================

# If there is more than this much time
# between messages, create a new session.

SESSION_GAP_MINUTES = 60


# ==========================================
# 5. BUILD SESSIONS
# ==========================================

sessions = []

current_session = []

previous_time = None


for message in messages:

    timestamp = message.get("timestamp")

    if not timestamp:
        continue

    current_time = parse_timestamp(timestamp)


    # ======================================
    # FIRST MESSAGE
    # ======================================

    if previous_time is None:

        current_session.append(message)

        previous_time = current_time

        continue


    # ======================================
    # CALCULATE GAP
    # ======================================

    gap_minutes = (
        current_time - previous_time
    ).total_seconds() / 60


    # ======================================
    # NEW SESSION
    # ======================================

    if gap_minutes > SESSION_GAP_MINUTES:

        if current_session:

            sessions.append(current_session)

        current_session = [message]


    # ======================================
    # SAME SESSION
    # ======================================

    else:

        current_session.append(message)


    previous_time = current_time


# ==========================================
# 6. SAVE LAST SESSION
# ==========================================

if current_session:

    sessions.append(current_session)


# ==========================================
# 7. CONVERT TO STRUCTURED FORMAT
# ==========================================

structured_sessions = []


for index, session in enumerate(sessions, start=1):

    start_time = session[0]["timestamp"]
    end_time = session[-1]["timestamp"]

    senders = list({
        message["sender"]
        for message in session
        if message.get("sender")
    })

    structured_sessions.append({

        "session_id": index,

        "start_time": start_time,

        "end_time": end_time,

        "message_count": len(session),

        "participants": senders,

        "messages": session
    })


# ==========================================
# 8. SAVE
# ==========================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(
        structured_sessions,
        file,
        ensure_ascii=False,
        indent=2
    )


# ==========================================
# 9. STATISTICS
# ==========================================

session_lengths = [
    session["message_count"]
    for session in structured_sessions
]


total_sessions = len(structured_sessions)

average_messages = (
    sum(session_lengths) / total_sessions
    if total_sessions
    else 0
)

largest_session = (
    max(session_lengths)
    if session_lengths
    else 0
)


# ==========================================
# 10. REPORT
# ==========================================

print()
print("=" * 60)
print("              CONVERSATION SESSIONS")
print("=" * 60)

print()

print(f"Total sessions          : {total_sessions}")

print(
    f"Average messages/session: "
    f"{average_messages:.2f}"
)

print(
    f"Largest session         : "
    f"{largest_session} messages"
)


print()
print("FIRST 10 SESSIONS")
print("-" * 60)


for session in structured_sessions[:10]:

    print()

    print(
        f"Session {session['session_id']}"
    )

    print(
        f"Start       : "
        f"{session['start_time']}"
    )

    print(
        f"End         : "
        f"{session['end_time']}"
    )

    print(
        f"Messages    : "
        f"{session['message_count']}"
    )

    print(
        f"Participants: "
        f"{', '.join(session['participants'])}"
    )


print()
print("=" * 60)
print("✅ SESSION ANALYSIS COMPLETED")
print("=" * 60)

print(
    f"Saved to: {OUTPUT_FILE}"
)