import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv(
    "EZVIZ_API_URL",
    "https://open.ezvizlife.com/api/lapp/live/address/get"
)
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
SERIAL_CAMARA = os.getenv("SERIAL_CAMARA", "D12639530")
CHANNEL = os.getenv("CHANNEL", "1")
PROTOCOL = os.getenv("PROTOCOL", "2")
QUALITY = os.getenv("QUALITY", "1")
