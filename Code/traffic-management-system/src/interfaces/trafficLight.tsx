interface TrafficLight {
    current_phase: number;
    location: {
      latitude: number;
      longitude: number;
    };
    name: string;
    phase_timings: number[];
    junction_id: string;
  }