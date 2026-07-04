import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

interface TrafficLight {
  junction_id: string;
  phase_timings: number[];
}

interface OverlayMenuProps {
  position: { top: number, left: number };
  name: string;
  trafficLight: TrafficLight;
  onClose: () => void;
}

const overlayStyle: React.CSSProperties = {
  position: 'absolute',
  background: 'white',
  boxShadow: '0px 0px 10px rgba(0, 0, 0, 0.1)',
  padding: '10px',
  zIndex: 1100,
  borderRadius: '5px',
  transform: 'scale(0.9)',
  transition: 'opacity 0.3s ease, transform 0.3s ease'
};

const buttonStyle: React.CSSProperties = {
  display: 'block',
  width: '100%',
  padding: '10px',
  margin: '5px 0',
  backgroundColor: '#62a8ea', // lighter blue
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  transition: 'background-color 0.3s ease',
};

const buttonHoverStyle: React.CSSProperties = {
  backgroundColor: '#8fc9ff' // even lighter blue
};

const clickedButtonStyle: React.CSSProperties = {
  backgroundColor: '#28a745' // green
};

const OverlayMenu: React.FC<OverlayMenuProps> = ({ position, name, trafficLight, onClose }) => {
  const [clickedButton, setClickedButton] = useState<number | null>(null);

  const handlePhaseClick = (phaseIndex: number) => {
    setClickedButton(phaseIndex);

    fetch(`http://127.0.0.1:5000/change_phase`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ junction_id: trafficLight.junction_id, phase: phaseIndex }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Request success:', data);
    })
    .catch(error => {
      console.error('Request error:', error);
    });

    // Revert the button color after a short period
    setTimeout(() => {
      setClickedButton(null);
    }, 500); // Change the timeout duration as needed
  };

  return (
    <div style={{ ...overlayStyle, top: position.top, left: position.left }}>
      <button onClick={onClose} style={{ float: 'right', background: 'none', border: 'none', cursor: 'pointer' }}>
        <X />
      </button>
      <h4>{name}</h4>
      {trafficLight.phase_timings.map((timing, index) => (
        <button
          key={index}
          style={index === clickedButton ? { ...buttonStyle, ...clickedButtonStyle } : buttonStyle}
          onMouseOver={e => e.currentTarget.style.backgroundColor = buttonHoverStyle.backgroundColor as string}
          onMouseOut={e => e.currentTarget.style.backgroundColor = index === clickedButton ? clickedButtonStyle.backgroundColor as string : buttonStyle.backgroundColor as string}
          onClick={() => handlePhaseClick(index)}
        >
          Phase {index + 1}
          {/* : {timing} seconds */}
        </button>
      ))}
    </div>
  );
}

export default OverlayMenu;
