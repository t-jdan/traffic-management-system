import os
import sys
import traci
import asyncio
import websockets
import json

# Ensure the SUMO_HOME environment variable is set
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

# Define the SUMO command and config file
sumocfg_path = "C:/Users/University/OneDrive - Ashesi University/4th Year/Capstone/Final Project/2024-07-18-02-25-27/osm.sumocfg"
sumoCmd = ["sumo-gui", "-c", sumocfg_path, "--delay", "1000"]

# Create an asyncio event for synchronization
action_event = asyncio.Event()
current_action = None

async def run_sumo():
    global current_action
    traci.start(sumoCmd)
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1

        # Process the current action if available
        if current_action:
            process_action(current_action)
            current_action = None
            action_event.clear()  # Reset the event

        await asyncio.sleep(0.1)  # Adjust the sleep time as necessary
    traci.close()

def map_phase(phase):
    # Map the incoming phase (0, 1, 2, 3) to TraCI phase (0, 2, 4, 6)
    return phase * 2

def process_action(action):
    try:
        action_data = json.loads(action)
        if action_data['action'] == "change_phase":
            junction_id = action_data['junction_id']
            target_phase = map_phase(action_data['phase'])
            current_phase = traci.trafficlight.getPhase(junction_id)

            # Only proceed if the current phase is not the target phase
            if current_phase != target_phase:
                # Determine the corresponding yellow phase
                yellow_phase = current_phase + 1 if current_phase % 2 == 0 else current_phase
                
                # Move to yellow phase if not already in yellow
                if current_phase != yellow_phase:
                    traci.trafficlight.setPhase(junction_id, yellow_phase)
                    yellow_duration = traci.trafficlight.getPhaseDuration(junction_id)
                    for _ in range(int(yellow_duration / traci.simulation.getDeltaT())):
                        traci.simulationStep()
                
                # Move to the target phase
                traci.trafficlight.setPhase(junction_id, target_phase)
        # Add more actions here
            
    except Exception as e:
        print(f"Error processing action: {e}")

async def handler(websocket, path):
    global current_action
    async for message in websocket:
        print(f"Received message: {message}")
        current_action = message
        action_event.set()  # Signal that an action is available
        await websocket.send(json.dumps({'status': 'action received'}))

async def main():
    sumo_task = asyncio.create_task(run_sumo())
    async with websockets.serve(handler, "localhost", 8765):
        await sumo_task

if __name__ == "__main__":
    asyncio.run(main())
