Github link: https://github.com/t-jdan/traffic-management-system

This system comprises of 3 systems, a web interface, a simulation and a machine learning model.

Web interface
To run the interface, react should be installed on the device. All the necessary code for the website will be in the traffic-management-system folder. When in that directory, type the command `npm run dev` in your terminal to launch the website. The API has to be running before the appropriate content of the website will load. The file for the flask API is labelled tms_api.py. There needs to be an accessible firebase database for the API to work.

Simulation
The Simulation was built using SUMO. To install sumo, refer to this link: https://sumo.dlr.de/docs/Installing/index.html
After installing, you can use the file named 'websocket.py' to launch the simulation. The file launches the SUMO program on the the same port the API uses. When all these files are running concurrently, the web interface should be able to control the simulation. In this system, the port used was 8813. 


Model
The model was trained using python. The necessary libraries are in the requirements.txt file. 'sumo-rl' was the major library used in training the simulation using SUMO. The documentation for using it can be found here: https://lucasalegre.github.io/sumo-rl/

