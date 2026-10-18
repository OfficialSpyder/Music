from telethon import TelegramClient
from telethon.sessions import StringSession

# Apne API Credentials yahan daalo
API_ID = int(input("Enter your API_ID: "))
API_HASH = input("Enter your API_HASH: ")

print("\n--- Generating Telethon String Session ---")
with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("\n✅ Successfully Logged In!")
    string_session = client.session.save()
    print("\nHere is your String Session (Copy this safely):")
    print("\n" + string_session + "\n")
    
    # Optional: File me bhi save kar dega
    with open("session.txt", "w") as f:
        f.write(string_session)
    print("💾 Session string has also been saved to session.txt!")