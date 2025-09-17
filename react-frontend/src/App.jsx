import { useState } from 'react'
import './App.css'
//import DrawingGate from './DrawingGate'

function App() {
  // const [verified, setVerified] = useState(false);

  const [N, setN] = useState(50);
  const [P, setP] = useState(30);
  const [K, setK] = useState(70);
  const [humidity, setHumidity] = useState(50);
  const [ph, setPh] = useState(30);
  const [rainfall, setRainfall] = useState(70);
  const [temperature, setTemperature] = useState(20);
  const [result, setResult] = useState(null);
  const [name, setName] = useState("")

  async function handlePredict() {
    try {
      const res = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ N, P, K, humidity, ph, rainfall, temperature, name }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Prediction failed", err);
    }
  }
/*
  if (!verified) {
    return (
      <div className="main">
        <h1>AI-check</h1>
        <p>För att komma in: rita rätt siffra.</p>
        <DrawingGate apiBase="http://localhost:5000" onPassed={() => setVerified(true)} />
      </div>
    );
  }*/

  return (
    <>
      <div className='main'>
        <label>Name: </label>
        <input onChange={(e) => setName(e.target.value)} type='textbox' />
        <div className='value-card'>
          <h2>Soil values</h2>

          <label>Nitrogen: {N}</label>
          <input type="range" min="0" max="140" step="1" value={N} onChange={(e) => setN(Number(e.target.value))} />

          <label>Phosphorus: {P}</label>
          <input type="range" min="5" max="145" step="1" value={P} onChange={(e) => setP(Number(e.target.value))} />

          <label>Potassium: {K}</label>
          <input type="range" min="5" max="205" step="1" value={K} onChange={(e) => setK(Number(e.target.value))} />
        </div>

        <div className='value-card'>
          <h2>Weather</h2>

          <label>Humidity: {humidity}</label>
          <input type="range" min="14.25" max="99.98" step="0.01" value={humidity} onChange={(e) => setHumidity(Number(e.target.value))} />

          <label>PH: {ph}</label>
          <input type="range" min="3.50" max="20.21" step="0.01" value={ph} onChange={(e) => setPh(Number(e.target.value))} />

          <label>Rainfall: {rainfall}</label>
          <input type="range" min="20.21" max="298.56" step="0.01" value={rainfall} onChange={(e) => setRainfall(Number(e.target.value))} />

          <label>Temp: {temperature}</label>
          <input type="range" min="8.82" max="43.67" step="0.01" value={temperature} onChange={(e) => setTemperature(Number(e.target.value))} />
        </div>

        <div>
          <button className='btnPredict' onClick={handlePredict}>Predict</button>
        </div>

        {result && (
          <div className="result-card">
            <h2>Prediction Result</h2>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    </>
  )
}

export default App
