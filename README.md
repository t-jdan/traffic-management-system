# Traffic Management System

GitHub: https://github.com/t-jdan/traffic-management-system

This system comprises 3 components: a web interface, a simulation, and a machine learning model.

## Web interface

All the necessary code for the website is in the `Code/traffic-management-system` folder. React must be installed on the device to run it. From that directory, run:

```bash
npm run dev
```

The Flask API (`Code/tms_api.py`) must be running before the website's content will load, and it requires an accessible Firebase database (`Code/keys/firebase_key.json`) to work.

## Simulation

The simulation was built using SUMO. To install SUMO, refer to [the installation docs](https://sumo.dlr.de/docs/Installing/index.html).

After installing, use `Code/web_socket.py` to launch the simulation. This file is responsible for running SUMO while connected to the API, ensuring the simulation can run while accepting requests to change it. It launches SUMO on the same port the API uses (port 8813). When all these files are running concurrently, the web interface can control the simulation.

## Model

The model was trained using Python. The necessary libraries are listed in `Code/requirements.txt`. [`sumo-rl`](https://lucasalegre.github.io/sumo-rl/) was the major library used to train the model against the SUMO simulation.

## Demo

See [Demo/README.md](Demo/README.md) for a link to the demo video.
