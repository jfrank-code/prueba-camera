# EZVIZ Camera Isolation Test

This is a deliberately minimal version of VIGIL-AE.

It tests only:

    Browser
       ↓
    Frontend
       ↓
    FastAPI
       ↓
    EZVIZ API
       ↓
    HLS .m3u8

There is NO YOLO, ANPR, OCR, blockchain, Twilio, OpenCV or camera-processing pipeline.

## 1. Backend local test

Open a terminal:

    cd backend

Create `.env` from `.env.example` and put your real EZVIZ token there.

Install:

    pip install -r requirements.txt

Run:

    uvicorn main:app --reload --port 8080

Then open:

    http://localhost:8080/api/camera

A successful response should contain:

    "code": "200"
    "stream_url": "https://...m3u8..."

## 2. Frontend local test

Open another terminal:

    cd frontend
    npm install

Create `.env`:

    VITE_BACKEND_URL=http://localhost:8080

Run:

    npm run dev

Open the Vite URL shown in the terminal.

## 3. Railway

Deploy the `backend` folder as a Railway service.

Set these Railway variables:

    ACCESS_TOKEN=your_real_token
    SERIAL_CAMARA=D12639530
    CHANNEL=1
    PROTOCOL=2
    QUALITY=1

The backend listens on Railway's PORT automatically only if Railway supplies 8080; this test Dockerfile exposes 8080.

For the cleanest first test, the important endpoint is:

    https://YOUR-RAILWAY-DOMAIN/api/camera

## What the result means

### code 200 + stream_url
Railway can authenticate with EZVIZ and obtain the live stream URL.

### code 10002
EZVIZ is rejecting the token as seen from Railway. The token itself, account/session behavior, API environment, or EZVIZ-side restrictions then need investigation.

### timeout / request error
The problem is connectivity from Railway to EZVIZ.

### code 200 but frontend cannot play
The EZVIZ API connection works. The remaining problem is HLS/browser playback, not authentication.

### Important
The diagnostic never prints the complete access token. It only prints length, first/last characters and SHA-256.
