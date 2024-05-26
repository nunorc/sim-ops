
from so.ground_station import GroundStationState, GroundStationSim
from so.spacecraft import SpacecraftSim
from .shared import scenario, _is_jsonable

def test_ground_station_state():
    state = GroundStationState()

    assert isinstance(state, GroundStationState) == True

def test_ground_station_sim():
    gs_sim = GroundStationSim(scenario)

    assert isinstance(gs_sim, GroundStationSim) == True

def test_ground_station_sim_ping():
    gs_sim = GroundStationSim(scenario)
    sc_sim = SpacecraftSim(scenario)

    _prev_state = gs_sim.state
    state = gs_sim.ping(gs_sim.state.ts + 10.0, sc_sim.state)

    assert state.ts > _prev_state.ts

    assert _is_jsonable(state.to_dict()) == True
