import sys
import pandas as pd
from parser import parse_chat

def main(filepath):
    # Read the chat file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find file at '{filepath}'")
        sys.exit(1)
        
    # Parse the messages using our parser
    messages = parse_chat(lines)
    
    if not messages:
        print("No messages could be parsed. Please check the file format.")
        return
        
    # Load into a pandas DataFrame for easy analysis
    df = pd.DataFrame(messages)
    
    # 1. Total messages
    total_messages = len(df)
    
    # 2. Unique senders
    unique_senders = df['sender'].nunique()
    
    # 3. Messages by sender
    sender_counts = df['sender'].value_counts()
    
    # 4. Average message length
    # Calculate length of each message and group by sender
    df['msg_length'] = df['message'].apply(len)
    avg_length = df.groupby('sender')['msg_length'].mean().round(2)
    
    # 5. Most active day
    most_active_day = df['date'].value_counts().idxmax()
    
    # 6. Most active hour
    # Extract just the hour part (e.g., '17:46' -> '17:00')
    df['hour'] = df['time'].str.split(':').str[0] + ":00"
    most_active_hour = df['hour'].value_counts().idxmax()
    
    # Print the final report
    print("========== PROJECT ECHO ==========\n")
    print(f"Total messages: {total_messages}\n")
    print(f"Unique senders: {unique_senders}\n")
    
    print("Messages by sender:\n")
    for sender, count in sender_counts.items():
        print(f"{sender}: {count}")
        
    print("\nAverage message length:\n")
    for sender, avg in avg_length.items():
        print(f"{sender}: {avg}")
        
    print(f"\nMost active day:\n{most_active_day}\n")
    print(f"Most active hour:\n{most_active_hour} is it??")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <path_to_whatsapp_export.txt>")
        sys.exit(1)
        
    main(sys.argv[1])
