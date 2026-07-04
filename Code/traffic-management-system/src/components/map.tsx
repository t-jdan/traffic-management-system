'use client'

import React, { useEffect, useState } from 'react';
import { Loader } from '@googlemaps/js-api-loader';
import Sidebar, { SidebarItem } from './sidebar';
import OverlayMenu from './dropdown';
import { AlignLeft, MapPin, SlidersHorizontal } from 'lucide-react';
import { ClipLoader } from 'react-spinners';


// Map component to display the map
export function Map() {
  const mapRef = React.useRef<HTMLDivElement>(null);
  const [isSidebarVisible, setIsSidebarVisible] = useState(true);
  const [trafficData, setTrafficData] = useState<TrafficLight[]>([]);
  const [map, setMap] = useState<google.maps.Map>();
  const [loading, setIsLoading] = useState(true);
  const [overlayPosition, setOverlayPosition] = useState<{ top: number, left: number } | null>(null);
  const [selectedTrafficLight, setSelectedTrafficLight] = useState<TrafficLight | null>(null);

  useEffect(() => {
    const fetchTrafficData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000');
        const data = await response.json();
        setTrafficData(data);
        initMap(data);
      } catch (err) {
        console.error('Error fetching traffic data:', err);
      }
    };

    const initMap = async (trafficData: TrafficLight[]) => {
      const loader = new Loader({
        apiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY as string,
        version: "weekly",
      });

      const { Map } = await loader.importLibrary('maps');
      const { AdvancedMarkerElement } = await loader.importLibrary('marker') as google.maps.MarkerLibrary;

      const position = { lat: 5.6269034, lng: -0.1764390 };

      const mapOptions: google.maps.MapOptions = {
        center: position,
        zoom: 14,
        mapId: '291007481d9b895f',
        mapTypeControl: true,
        streetViewControl: false,
        mapTypeControlOptions: {
          style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
          position: google.maps.ControlPosition.TOP_RIGHT,
        },
      }

      const map = new Map(mapRef.current as HTMLDivElement, mapOptions);
      setMap(map);

      trafficData.forEach(trafficLight => {
        const { latitude, longitude } = trafficLight.location;
        const position = { lat: latitude, lng: longitude };

        const markerContent = document.createElement('div');
        const markerImage = document.createElement('img');
        markerImage.src = "images/traffic-lights (1).png";
        markerImage.style.width = '50px';
        markerImage.style.height = '50px';
        markerContent.appendChild(markerImage);

        const marker = new AdvancedMarkerElement({
          position: position,
          map: map,
          title: trafficLight.name,
          content: markerContent,
          gmpClickable: true,
          gmpDraggable: false,
        });

        marker.addListener('click', (event: google.maps.MapMouseEvent) => {
          if (event.domEvent) {
            const { clientX, clientY } = event.domEvent as MouseEvent;
            setOverlayPosition({ top: clientY, left: clientX + 10 });
            setSelectedTrafficLight(trafficLight);
          }
        });

        marker.addListener('mouseover', () => {
          console.log('Marker mouseover:', trafficLight.name);
        });
      });

      map.addListener('click', () => {
        setOverlayPosition(null);
        setSelectedTrafficLight(null);
      });

      map.addListener('zoom_changed', () => {
        setOverlayPosition(null);
        setSelectedTrafficLight(null);
      });

      setIsLoading(false);
    };

    fetchTrafficData();
  }, []);

  const handleSidebarItemClick = () => {
    setOverlayPosition(null);
    setSelectedTrafficLight(null);
  };

  return (
    <div style={{ position: 'relative', height: '100vh', width: '100%' }}>
      {loading && (
        <div style={loadingStyle}>
          <ClipLoader color="#007BFF" size={50} loading={loading} />
        </div>
      )}
      <div ref={mapRef} style={{ height: '100%', width: '100%' }} />
      {isSidebarVisible && !loading && (
        <div style={sidebarOverlayStyle} onClick={handleSidebarItemClick}>
          <Sidebar>
            <SidebarItem
              icon={<AlignLeft size={20} />}
              text='Traffic Phases'
              active={false}
              alert={false}
            >
              <TrafficPhases trafficData={trafficData} />
            </SidebarItem>
            <SidebarItem
              icon={<MapPin size={20} />}
              text='Add Traffic Light'
              active={false}
              alert={false}
            />
            <SidebarItem
              icon={<SlidersHorizontal size={20} />}
              text='Automation Controls'
              active={false}
              alert={false}
            />
          </Sidebar>
        </div>
      )}
      {overlayPosition && selectedTrafficLight && (
        <OverlayMenu
          position={overlayPosition}
          name={selectedTrafficLight.name}
          trafficLight={selectedTrafficLight}
          onClose={() => {
            setOverlayPosition(null);
            setSelectedTrafficLight(null);
          }}
        />
      )}
    </div>
  );
}

const loadingStyle: React.CSSProperties = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  zIndex: 1000,
};

const sidebarOverlayStyle: React.CSSProperties = {
  position: 'absolute',
  top: 0,
  left: 0,
  height: '100%',
  zIndex: 1000,
};

const toggleButtonStyle: React.CSSProperties = {
  position: 'absolute',
  top: '10px',
  left: '260px',
  zIndex: 1100,
  padding: '10px 20px',
  backgroundColor: '#007BFF',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
};

// New TrafficPhases Component
function TrafficPhases({ trafficData }: { trafficData: TrafficLight[] }) {
  return (
    <div className="h-48 overflow-y-auto">
      {trafficData.map((trafficLight, index) => (
        <div key={index}>
          <h4 className="font-semibold">{trafficLight.name}</h4>
          <ul className="ml-4">
            {trafficLight.phase_timings.map((timing, phaseIndex) => (
              <li key={phaseIndex} className="py-1 px-2 hover:bg-gray-100">
                Phase {phaseIndex + 1}: {timing} seconds
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}


