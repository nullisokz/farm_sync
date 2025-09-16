import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [nitrogen, setNitrogen] = useState(50);
  const [phosphorus, setPhosphorus] = useState(30);
  const [potassium, setPotassium] = useState(70);
  const [humidity, setHumidity] = useState(50);
  const [ph, setPh] = useState(30);
  const [rainfall, setRainfall] = useState(70);
  const [result, setResult] = useState(null);

  async function handlePredict() {
    try {
      const res = await fetch("http://localhost:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nitrogen,
          phosphorus,
          potassium,
          humidity,
          ph,
          rainfall,
        }),
      });
      const data = await res.json();
      setResult(data); // <-- SPARA RESULTAT
    } catch (err) {
      console.error("Prediction failed", err);
    }
  }

  return (
    <>
      <div className='main'>
        <label>Name: </label><input type='textbox'></input>
        <div className='value-card'>
          <h2>Soil values</h2>
          <label>Nitrogen: {nitrogen}</label>
          <input
            type="range"
            min="0"
            max="140"
            step="1"
            value={nitrogen}
            onChange={(e) => setNitrogen(Number(e.target.value))}
          />

          <label>Phosphorus: {phosphorus}</label>
          <input
            type="range"
            min="5"
            max="145"
            step="1"
            value={phosphorus}
            onChange={(e) => setPhosphorus(Number(e.target.value))}
          />

          <label>Potassium: {potassium}</label>
          <input
            type="range"
            min="5"
            max="205"
            step="1"
            value={potassium}
            onChange={(e) => setPotassium(Number(e.target.value))}
          />
      </div>
      
      <div className='value-card'>
          <h2>Weather</h2>
          <label>Humidity: {humidity}</label>
          <input
            type="range"
            min="14.25803981"
            max="99.98187601"
            step="1"
            value={humidity}
            onChange={(e) => setHumidity(Number(e.target.value))}
          />

          <label>PH: {ph}</label>
          <input
            type="range"
            min="3.504752314"
            max="20.21126747"
            step="1"
            value={ph}
            onChange={(e) => setPh(Number(e.target.value))}
          />

          <label>Rainfall: {rainfall}</label>
          <input
            type="range"
            min="20.21126747"
            max="298.5601175"
            step="1"
            value={rainfall}
            onChange={(e) => setRainfall(Number(e.target.value))}
          />
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
