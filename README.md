# Multiagent Reinforcement Learning for traffic light signal control

Paper: <https://doi.org/10.1007/978-3-030-24209-1_10>

Demo: <https://www.youtube.com/watch?v=A-Uv344e8Bc>

## Testing
After you have installed [SUMO simulator](https://sumo.dlr.de/docs/index.html), you can test the following policies for the following network:
![](https://github.com/carolinahiguera/BogotaRL/blob/master/Testing/demo%20files/gui/img/map.svg)

* Fixed time policy
* Independent Q-Learning for every agent
* MARL with best response for coordination
* MARL with variable elimination algorithm
* Some state-of-the-art methods

In a terminal (run with Python3):

```
cd Testing/demo files/gui
python gui_demo.py
cd ../FT
python testTF.py
cd ../indeQ
python marl.py
cd ../brQ
python marl.py
cd ../veQ
python marl.py
cd ../xuQ
python marl.py
```
