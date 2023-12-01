import carla
from pynput import keyboard
import time
import sys
import argparse
import json
import zenoh
from zenoh import config, Sample, Value
from ast import literal_eval

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog='z_queryable',
    description='zenoh queryable example')
parser.add_argument('--mode', '-m', dest='mode',
                    choices=['peer', 'client'],
                    type=str,
                    help='The zenoh session mode.')
parser.add_argument('--connect', '-e', dest='connect',
                    metavar='ENDPOINT',
                    action='append',
                    type=str,
                    help='Endpoints to connect to.')
parser.add_argument('--listen', '-l', dest='listen',
                    metavar='ENDPOINT',
                    action='append',
                    type=str,
                    help='Endpoints to listen on.')
parser.add_argument('--key', '-k', dest='key',
                    default='traffic_light/**',
                    type=str,
                    help='The key expression matching queries to reply to.')
parser.add_argument('--value', '-v', dest='value',
                    default='ACK',
                    type=str,
                    help='The value to reply to queries.')
parser.add_argument('--complete', dest='complete',
                    default=False,
                    action='store_true',
                    help='Declare the queryable as complete w.r.t. the key expression.')
parser.add_argument('--config', '-c', dest='config',
                    metavar='FILE',
                    type=str,
                    help='A configuration file.')

args = parser.parse_args()
conf = zenoh.Config.from_file(args.config) if args.config is not None else zenoh.Config()
if args.mode is not None:
    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
if args.connect is not None:
    conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
if args.listen is not None:
    conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(args.listen))
key = args.key
value = args.value
complete = args.complete

def set_state(selector, new_state):
    global traffic_lights
    index = int(str(selector).split('/')[1])

    if new_state == 'green':
        for i in range(30, 33):
            if i != index:
                traffic_lights[i].set_state(carla.TrafficLightState.Red)
        traffic_lights[index].set_state(carla.TrafficLightState.Green)
    elif new_state == 'red':
        traffic_lights[index].set_state(carla.TrafficLightState.Red)

def get_state(selector):
    global traffic_lights

    index = str(selector).split('/')[1]
    state = traffic_lights[int(index)].get_state()

    return state
    

def queryable_callback(query):

    global traffic_lights

    print(f">> [Queryable ] Received Query '{query.selector}'" + (f" with value: {query.value.payload}" if query.value is not None else ""))
    # query.reply(Sample(key, value))

    if query.value is None:
        # Get traffic light state
        state = get_state(query.selector)
        query.reply(Sample(str(query.selector), state))
    else:
        new_state = query.value.payload.decode('utf-8')
        set_state(query.selector, new_state)

spec_id = 0

def on_press(k):
    try:
        pass
    except AttributeError:
        pass

def on_release(k):
    global spectator
    global spec_id

    if k == keyboard.Key.tab:
        spec_id += 1
        if spec_id == 4:
            spec_id = 0
        if spec_id == 0:
            spectator.set_transform(carla.Transform(
                carla.Location(x=83.918785, y=106.423500, z=6.480291), 
                carla.Rotation(pitch=-25.652645, yaw=73.435905, roll=-0.000030)))
        elif spec_id == 1:
            spectator.set_transform(carla.Transform(
                carla.Location(x=119.048515, y=133.816574, z=7.551385), 
                carla.Rotation(pitch=-23.294645, yaw=-172.816132, roll=-0.000031)))
        elif spec_id == 2:
            spectator.set_transform(carla.Transform(
                carla.Location(x=95.999725, y=157.935394, z=6.279342), 
                carla.Rotation(pitch=-19.706659, yaw=-110.011833, roll=-0.000030)))
        elif spec_id == 3:
            spectator.set_transform(carla.Transform(
                carla.Location(x=92.954048, y=132.297363, z=35.752739), 
                carla.Rotation(pitch=-88.975876, yaw=-179.735474, roll=0.000172)))
    elif k == keyboard.Key.esc:
        # Stop listener
        return False


# create a client in the Carla simulator
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.load_world('Town01')

settings = world.get_settings()
settings.synchronous_mode = True # Enables synchronous mode
settings.fixed_delta_seconds = 0.05
world.apply_settings(settings)

# Get traffic lights
traffic_lights = world.get_actors().filter("traffic.traffic_light")

spectator = world.get_spectator()
spectator.set_transform(carla.Transform(
    carla.Location(x=83.918785, y=106.423500, z=6.480291), 
    carla.Rotation(pitch=-25.652645, yaw=73.435905, roll=-0.000030)))


for i in range(30, 33):
    traffic_lights[i].set_red_time(1000.0)
    traffic_lights[i].set_green_time(5.0)
    traffic_lights[i].set_yellow_time(0.0)
    traffic_lights[i].set_state(carla.TrafficLightState.Red)

# initiate logging
zenoh.init_logger()

print("Opening session...")
session = zenoh.open(conf)

print("Declaring Queryable on '{}'...".format(key))
queryable = session.declare_queryable(key, queryable_callback, complete)

# keyboard control listener
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

print("--------------------------------")
print("| ESC : exit controller.       |")
print("| TAB : change perspective.    |")
print("--------------------------------")

def main(args):
    sync = True
    try:
        while listener.is_alive():
            if sync:
                world.tick()
            else:
                world.wait_for_tick()
    finally:
        if sync:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)
        
        queryable.undeclare()
        session.close()
        print('\rdestroying vehicles')
        # ego_vehicle.destroy()
        time.sleep(0.5)



if __name__ == '__main__':

    try:
        main(args)
    except KeyboardInterrupt:
        pass
    finally:
        print('done.')
