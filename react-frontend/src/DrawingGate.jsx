import { useEffect, useRef, useState } from "react";

export default function DrawingGate({ apiBase = "http://localhost:5000", onPassed }) {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [target, setTarget] = useState(() => Math.floor(Math.random() * 10));
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const c = canvasRef.current;
    const ctx = c.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.lineWidth = 18;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "#000000";
  }, []);

  function getPos(e) {
    const rect = canvasRef.current.getBoundingClientRect();
    const client = e.touches ? e.touches[0] : e;
    return { x: client.clientX - rect.left, y: client.clientY - rect.top };
    }

  function handleDown(e) {
    e.preventDefault();
    setIsDrawing(true);
    const ctx = canvasRef.current.getContext("2d");
    const { x, y } = getPos(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
  }

  function handleMove(e) {
    if (!isDrawing) return;
    e.preventDefault();
    const ctx = canvasRef.current.getContext("2d");
    const { x, y } = getPos(e);
    ctx.lineTo(x, y);
    ctx.stroke();
  }

  function handleUp() { setIsDrawing(false); }

  function clearCanvas() {
    const c = canvasRef.current;
    const ctx = c.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, c.width, c.height);
  }

  async function submitDrawing() {
    try {
      setLoading(true);
      setMsg("");

      // Skala till 28x28 PNG dataURL
      const src = canvasRef.current;
      const small = document.createElement("canvas");
      small.width = 28; small.height = 28;
      const sctx = small.getContext("2d");
      sctx.fillStyle = "#ffffff"; sctx.fillRect(0, 0, 28, 28);
      sctx.drawImage(src, 0, 0, 28, 28);
      const dataUrl = small.toDataURL("image/png");

      const res = await fetch(`${apiBase}/mnist/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataUrl, target_digit: target, threshold: 0.85 }),
      });
      const data = await res.json();

      if (data.status === "success") {
        if (data.passed) {
          setMsg(`✅ Rätt! ${data.pred} (p=${data.prob.toFixed(2)}).`);
          onPassed?.();
        } else {
          setMsg(`❌ Blev ${data.pred} (p=${data.prob?.toFixed(2) ?? "–"}). Försök igen!`);
        }
      } else {
        setMsg(`Fel: ${data.error || "okänt fel"}`);
      }
    } catch (err) {
      console.error(err);
      setMsg("Nätverksfel.");
    } finally {
      setLoading(false);
    }
  }

  function newTarget() {
    setTarget(Math.floor(Math.random() * 10));
    clearCanvas();
    setMsg("");
  }

  return (
    <div className="gate-wrap">
      <h2>Rita siffran: <span className="gate-target">{target}</span></h2>
      <canvas
        ref={canvasRef}
        width={280}
        height={280}
        className="gate-canvas"
        onMouseDown={handleDown}
        onMouseMove={handleMove}
        onMouseUp={handleUp}
        onMouseLeave={handleUp}
        onTouchStart={handleDown}
        onTouchMove={handleMove}
        onTouchEnd={handleUp}
      />
      <div className="gate-actions">
        <button onClick={clearCanvas} disabled={loading}>Rensa</button>
        <button onClick={newTarget} disabled={loading}>Ny siffra</button>
        <button onClick={submitDrawing} disabled={loading}>{loading ? "Kollar…" : "Skicka"}</button>
      </div>
      {msg && <p className="gate-msg">{msg}</p>}
      <p className="gate-hint">Tips: Rita med tjocka, sammanhängande streck.</p>
    </div>
  );
}
