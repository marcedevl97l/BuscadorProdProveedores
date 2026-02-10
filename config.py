import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.getenv("DB_PATH", os.path.join(BASE_DIR, "db.sqlite"))
