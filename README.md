# traffic_light_control
It's a developing tool for traffic light's state controller in CARLA simulator.

## Prerequisites
python 3.8

carla 0.9.13

## Build
```bash=
bash ./script/download_map.sh
```

## Usage
- Step 1:
```bash=
./CarlaUE4.sh -world-port=2000
```
- Step 2:
```bash=
python main.py
```
- Step 3:
```bash=
python controller.py --cmd <get/set> -i <light_id> -s <light_state>
```

