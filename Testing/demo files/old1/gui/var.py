START_TIME = 6

NUM_ROUTES = 4

PIPES_NAMES = [
                '/tmp/sumo_tf',
                # '/tmp/sumo_indQ',
                #'/tmp/sumo_brQ',
                #'/tmp/sumo_indB',
                #'/tmp/sumo_indC',
               ]

METHODS_NAMES = [
                'Fixed Times',
                # 'Independent Q-Learning',
                #'MARL best response',
                #'Other 2',
                #'Other 3',
]

if len(PIPES_NAMES) != len(METHODS_NAMES):
    print('Error: PIPES_NAMES and METHODS_NAMES must have the same length')
    exit(1)

NUM_TRAVEL_TIME_COLS = 2
NUM_GREEN_WAVES_COLS = 2
GREEN_WAVES_FT = True

NUM_METHODS = len(PIPES_NAMES)

COLOR_METHODS = ['r', 'y', 'b', 'g', 'r']



DEF_PLOT_WINDOW = 0
PLOT_WINDOWS = [
    {'mins':20, 'label':'20 mins'},
    {'mins':60, 'label':'1 hour'},
    {'mins':2*60, 'label':'2 hours'},
    {'mins':6*60, 'label':'6 hours'},
    {'mins':12*60, 'label':'12 hours'},
    {'mins':24*60, 'label':'24 hours'}
]

DEF_SIM_SPEED = 0
SIM_SPEEDS = [
    {'secs':0, 'label':'max'},
    {'secs':0.01, 'label':'x100'},
    {'secs':0.1, 'label':'x10'},
    {'secs':1, 'label':'x1'},
]

TEST_ROUTE = {
    'route_agents': [5, 4, 3],
    'agent_indexes': {5:0, 4:1, 3:2},
    'route_edge': {5:'A5N', 4:'A4N', 3:'A3N'},
    'route_edges_i': {5:0, 4:0, 3:0},
    'route_edges_len': {5:114.56, 4:116.97, 3:129.71},
    'name': 'Route 1: Ak7 North-South'
}

INITIAL_AGENTS_STATE = [0, 0, 0]

if len(TEST_ROUTE['route_agents']) != len(INITIAL_AGENTS_STATE):
    print("Error: TEST_ROUTE['route_agents'] and INITIAL_AGENTS_STATE must have the same length")
    exit(1)