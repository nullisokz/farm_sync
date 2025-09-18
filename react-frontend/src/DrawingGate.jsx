import { useEffect, useRef, useState } from "react";
import { API_BASE } from "./lib/apiBase";

export default function DrawingGate({ apiBase = API_BASE, onPassed }) {
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

      const src = canvasRef.current;
      const small = document.createElement("canvas");
      small.width = 28; small.height = 28;
      const sctx = small.getContext("2d");
      sctx.fillStyle = "#ffffff"; sctx.fillRect(0, 0, 28, 28);
      sctx.drawImage(src, 0, 0, 28, 28);
      const dataUrl = small.toDataURL("image/png");

      const res = await fetch(`${apiBase}/api/mnist/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataUrl, target_digit: target, threshold: 0.85 }),
      });
      const data = await res.json();

      if (data.status === "success") {
        if (data.passed) {
          setMsg(`✅ Correct! ${data.pred} (p=${data.prob.toFixed(2)}).`);
          onPassed?.();
        } else {
          setMsg(`❌ Incorrect! ${data.pred} (p=${data.prob?.toFixed(2) ?? "–"}). Try again!`);
        }
      } else {
        setMsg(`Error: ${data.error || "Unknown error"}`);
      }
    } catch (err) {
      console.error(err);
      setMsg("Network error.");
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
      <h2>Draw the number: <span className="gate-target">{target}</span></h2>
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
        <button onClick={clearCanvas} disabled={loading}>Clear</button>
        <button onClick={newTarget} disabled={loading}>New Number</button>
        <button onClick={submitDrawing} disabled={loading}>{loading ? "Checking…" : "Submit"}</button>
      </div>
      {msg && <p className="gate-msg">{msg}</p>}
      <p className="gate-hint">Tip: Draw with thick, continuous lines.</p>
    </div>
  );
}
