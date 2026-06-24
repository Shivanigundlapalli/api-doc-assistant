import os
from dotenv import load_dotenv

print("CWD:", os.getcwd())
print("Files in CWD:", os.listdir(os.getcwd()))

# Before loading dotenv
print("KEY BEFORE dotenv:", repr(os.getenv("GOOGLE_API_KEY")))

load_dotenv()

print("KEY AFTER dotenv:", repr(os.getenv("GOOGLE_API_KEY")))

