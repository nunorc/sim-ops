
import json

from so.core import GroundStation, Scenario

ground_station = GroundStation(
    name = 'Darmstadt',
    latitude = 49.8718,
    longitude= 8.6224,
    altitude=127
)

scenario = Scenario(
    name = 'testing-0',
    begin = '2023-08-27 04:40:00+00:00',
    end = '2023-08-27 04:55:00+00:00',
    tle =  'OPS-SAT\n1 44878U 19092F   23237.49766723  .00030600  00000-0  81781-3 0  9990\n2 44878  97.4743  67.3096 0007340 241.3055 118.7452 15.38003807204438',
    time_step = 1,
    running = False,
    ground_station = ground_station
)

def _is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except:
        return False
