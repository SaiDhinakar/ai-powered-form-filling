import React from "react";
import "./App.css";
import Preview from './preview.jsx';

function App() {
  return (
    <div className="container">
      {/* Left side: Title only */}
      <div className="left">
        <h1>AI-Auto Form Filler</h1>
      </div>

      {/* Right side: Form options */}
      <div className="right">
        <div className="form-box">
          <label>Choose Government Form:</label>
          <select>
            <option>Select Form</option>
            <option>Passport</option>
            <option>Aadhaar</option>
            <option>PAN</option>
            <option>Voter ID</option>
            <option>Driver License</option>
            <option>Income Certificate</option>
            <option>Marriage Certificate</option>
            <option>Disability Certificate</option>
            <option>Senior Citizen Certificate</option>
            <option>GST Registration</option>
            <option>Ration Card</option>
            
          </select>
          <Preview/>
          <button>Fill Form</button>
        </div>
      </div>
    </div>
  );
}

export default App;