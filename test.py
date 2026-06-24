from dotenv import load_dotenv
import os

load_dotenv()

print("KEY:", repr(os.getenv("GOOGLE_API_KEY")))
