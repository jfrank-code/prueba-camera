import os
import time
import hashlib
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

app = FastAPI(title="EZVIZ Camera Test")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def token_debug(token: str):
    return {
        "present": bool(token),
        "length": len(token),
        "sha256": hashlib.sha256(token.encode()).hexdigest() if token else "",
        "start": token[:8] if token else "",
        "end": token[-8:] if token else "",
    }

def obtener_enlace_ezviz():
    token = os.getenv("ACCESS_TOKEN", ACCESS_TOKEN)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    payload = {
        "accessToken": token,
        "deviceSerial": SERIAL_CAMARA,
        "channelNo": str(CHANNEL),
        "protocol": int(PROTOCOL),
        "quality": int(QUALITY),
    }

    debug = token_debug(token)

    print("\n" + "=" * 70)
    print("EZVIZ CAMERA TEST")
    print("=" * 70)
    print("API:", API_URL)
    print("Device:", SERIAL_CAMARA)
    print("Channel:", CHANNEL)
    print("Protocol:", PROTOCOL)
    print("Quality:", QUALITY)
    print("Token present:", debug["present"])
    print("Token length:", debug["length"])
    print("Token SHA256:", debug["sha256"])
    print("Public IP check will be attempted...")

    public_ip = None
    try:
        ip_response = requests.get("https://api.ipify.org?format=json", timeout=5)
        if ip_response.ok:
            public_ip = ip_response.json().get("ip")
            print("Railway public IP:", public_ip)
    except Exception as e:
        print("Public IP check failed:", e)

    started = time.time()

    try:
        response = requests.post(
            API_URL,
            data=payload,
            headers=headers,
            timeout=15,
        )

        elapsed = round((time.time() - started) * 1000)

        print("HTTP:", response.status_code)
        print("Content-Type:", response.headers.get("content-type"))
        print("Elapsed:", elapsed, "ms")
        print("EZVIZ response:", response.text[:3000])

        try:
            result = response.json()
        except Exception:
            result = {
                "code": "INVALID_JSON",
                "msg": "EZVIZ did not return valid JSON",
                "raw": response.text[:3000],
            }

        code = str(result.get("code", ""))

        if code == "200":
            data = result.get("data") or {}
            url = data.get("url")

            if url:
                print("SUCCESS: EZVIZ returned an HLS URL.")
            else:
                print("EZVIZ returned code 200 but no data.url.")

        elif code == "10002":
            print("EZVIZ REJECTED THE ACCESS TOKEN.")

        else:
            print("EZVIZ returned another code:", code)

        print("=" * 70 + "\n")

        return {
            "ok": code == "200" and bool((result.get("data") or {}).get("url")),
            "code": code,
            "message": result.get("msg"),
            "stream_url": (result.get("data") or {}).get("url"),
            "expire_time": (result.get("data") or {}).get("expireTime"),
            "id": (result.get("data") or {}).get("id"),
            "http_status": response.status_code,
            "elapsed_ms": elapsed,
            "public_ip": public_ip,
            "token": debug,
            "device": SERIAL_CAMARA,
            "channel": CHANNEL,
            "api_url": API_URL,
            "raw": result,
        }

    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "code": "TIMEOUT",
            "message": "Timeout connecting to EZVIZ",
            "token": debug,
            "device": SERIAL_CAMARA,
            "channel": CHANNEL,
            "api_url": API_URL,
            "public_ip": public_ip,
        }

    except requests.exceptions.RequestException as e:
        return {
            "ok": False,
            "code": "REQUEST_ERROR",
            "message": str(e),
            "token": debug,
            "device": SERIAL_CAMARA,
            "channel": CHANNEL,
            "api_url": API_URL,
            "public_ip": public_ip,
        }

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/camera")
def camera():
    return obtener_enlace_ezviz()

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
      <head><title>EZVIZ Camera Test</title></head>
      <body style="font-family:Arial;padding:30px">
        <h1>EZVIZ Camera Test</h1>
        <p>Use <a href="/api/camera">/api/camera</a> to test EZVIZ.</p>
      </body>
    </html>
    """
