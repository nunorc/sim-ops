
# Sim-Ops

Sim-Ops is software suite for running spacecraft operations simulations exercises and demonstrations. It includes
a minimalist spacecraft simulator, a ground station simulator and a Monitoring and Control System (MCS).
Note, that the software suite is under constant development so things change fast. The following video
illustrates the MCS UI.

https://github.com/nunorc/sim-ops/assets/118554/2ff0d284-ef00-4299-83dd-374d9f3339cc

Repository content:

* `sim-ops-lib/`: Python packages to run in the background, including API and simulators.
* `sim-ops-mcs/`: MCS frontend interface.
* `containers/`: containers files and configurations.

The following scripts are required to be running:

* `so-master.py`: the master script managing the simulations in the background.
* `so/api.py`: the API required for the web interface.

### Run using Docker

Run using [Docker](https://www.docker.com/) containers, recommended, make sure to set the required
content in the `.env` file, or by using the option `--env-file`, for example to use the `.env.local` run:

    sim-ops$ docker compose --env-file .env.local build
    sim-ops$ docker compose --env-file .env.local up
    # mcs is available from http://localhost:8080

The default credentials for the basic authentication are:

    Username: sim
    Password: ops

The default password for the admin section in the MCS is `admin`.
In case you are running behind a reverse proxy, firewall, or any similar setting you may need to update the values
described in `.env.local` to your needs.

### Run from the command line

A Python (version 3.11 recommended) needs to be available, the list of required packages is available from `sim-ops-lib/requirements.txt` file.

**Note** A MQTT service, e.g. [Eclipse Mosquitto](https://mosquitto.org/) to run the scripts from a command line, check `containers/mqtt/config/mosquitto.conf` for an example configuration

Once an MQTT is running and reachable and all the requirements installed, run:

    # setup environment variables (required for all scripts and npm)
    sim-ops$ . scripts/export.env.dev.sh .env.local

    sim-ops$ cd sim-ops-lib

    # run master script
    sim-ops-lib$ python so-master.py

    # run api
    sim-ops-lib$ uvicorn so.api:app

    sim-ops$ cd sim-ops-mcs
    
    # run mcs
    sim-ops-mcs$ npm run dev
    # mcs is available from http://localhost:5173

Running Python lib tests:

    $ cd sim-ops-lib
    sim-ops-lib$ pytest

### The Sim-Ops Team

Nuno Carvalho, Peter Stöferle, Adrian Calleja, Vladimir Zelenevskiy, Rodrigo Laurinovics, Marcin Kovalevskij, Tim Oerther, Frederik Dall'Omo and David Evans.

### Acknowledgements

MCS UI theme based on HUD Vue by Sean Ngu.
