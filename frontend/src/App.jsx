import React, { useEffect, useRef, useState } from "react";
import Hls from "hls.js";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080";

function App() {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);

  const [status, setStatus] = useState("IDLE");
  const [diagnostic, setDiagnostic] = useState(null);
  const [error, setError] = useState("");

  async function connectCamera() {
    setError("");
    setStatus("CONNECTING");
    setDiagnostic(null);

    try {
      const response = await fetch(`${API_BASE}/api/camera`);
      const result = await response.json();

      setDiagnostic(result);

      if (!result.ok || !result.stream_url) {
        setStatus("EZVIZ ERROR");
        setError(
          `${result.code || "UNKNOWN"} — ${result.message || "No stream URL returned"}`
        );
        return;
      }

      const video = videoRef.current;
      const url = result.stream_url;

      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }

      if (Hls.isSupported()) {
        const hls = new Hls({
          enableWorker: true,
          lowLatencyMode: true,
        });

        hlsRef.current = hls;

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          video.play()
            .then(() => setStatus("LIVE"))
            .catch(() => setStatus("STREAM RECEIVED"));
        });

        hls.on(Hls.Events.ERROR, (_, data) => {
          console.error("HLS error:", data);
          if (data.fatal) {
            setStatus("HLS ERROR");
            setError(`${data.type}: ${data.details}`);
          }
        });

        hls.loadSource(url);
        hls.attachMedia(video);
      } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
        video.src = url;
        video.onloadedmetadata = () => {
          video.play()
            .then(() => setStatus("LIVE"))
            .catch(() => setStatus("STREAM RECEIVED"));
        };
      } else {
        setStatus("HLS UNSUPPORTED");
        setError("This browser does not support HLS playback.");
      }

    } catch (err) {
      console.error(err);
      setStatus("BACKEND ERROR");
      setError(err.message);
    }
  }

  useEffect(() => {
    connectCamera();

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
      }
    };
  }, []);

  const statusClass =
    status === "LIVE"
      ? "live"
      : status.includes("ERROR")
      ? "error"
      : "waiting";

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <div className="brand">VIGIL-AE</div>
          <div className="subtitle">EZVIZ CAMERA ISOLATION TEST</div>
        </div>

        <div className={`status ${statusClass}`}>
          <span className="dot"></span>
          {status}
        </div>
      </header>

      <main className="main">
        <section className="camera-card">
          <div className="camera-header">
            <div>
              <div className="camera-title">CAMERA 01</div>
              <div className="camera-location">EZVIZ · CHANNEL 1</div>
            </div>

            <button onClick={connectCamera}>
              RECONNECT
            </button>
          </div>

          <div className="video-wrapper">
            <video
              ref={videoRef}
              controls
              muted
              playsInline
              autoPlay
            />

            {status !== "LIVE" && (
              <div className="video-overlay">
                <div className="spinner"></div>
                <div>{status}</div>
              </div>
            )}
          </div>
        </section>

        <section className="diagnostics">
          <div className="section-title">CONNECTION DIAGNOSTICS</div>

          <div className="grid">
            <Info label="EZVIZ API" value={diagnostic?.http_status || "—"} />
            <Info label="EZVIZ CODE" value={diagnostic?.code || "—"} />
            <Info label="DEVICE" value={diagnostic?.device || "—"} />
            <Info label="CHANNEL" value={diagnostic?.channel || "—"} />
            <Info label="LATENCY" value={diagnostic?.elapsed_ms ? `${diagnostic.elapsed_ms} ms` : "—"} />
            <Info label="PUBLIC IP" value={diagnostic?.public_ip || "—"} />
            <Info label="TOKEN" value={diagnostic?.token?.present ? "PRESENT" : "MISSING"} />
            <Info label="STREAM URL" value={diagnostic?.stream_url ? "RECEIVED" : "NOT RECEIVED"} />
          </div>

          {error && (
            <div className="error-box">
              <strong>ERROR</strong>
              <div>{error}</div>
            </div>
          )}

          {diagnostic?.message && !error && (
            <div className="message-box">
              EZVIZ: {diagnostic.message}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="info">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  );
}

export default App;
