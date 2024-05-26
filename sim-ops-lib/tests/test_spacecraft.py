
from so.spacecraft import SpacecraftState, SpacecraftSim
from .shared import scenario, _is_jsonable

def test_spacecraft_state():
    state = SpacecraftState()

    assert isinstance(state, SpacecraftState) == True

def test_spacecraft_sim():
    sc_sim = SpacecraftSim(scenario)

    assert isinstance(sc_sim, SpacecraftSim) == True

def test_spacecraft_sim_ping():
    sc_sim = SpacecraftSim(scenario)

    _prev_state = sc_sim.state
    state = sc_sim.ping(sc_sim.state.ts + 10.0)

    assert state.ts > _prev_state.ts

    assert _is_jsonable(state.to_dict()) == True
