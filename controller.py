import carla
from pynput import keyboard
import time


light_state = carla.TrafficLightState.Red
spec_id = 0

def on_press(key):
    try:
        pass
    except AttributeError:
        pass

def on_release(key):
    global traffic_lights
    global spectator
    global spec_id
    try:
        print(' \r', end="")
        if key.char == 'r':
            # light_state = carla.TrafficLightState.Red
            for i in range(30, 33):
                traffic_lights[i].set_state(carla.TrafficLightState.Red)
            print("Set Traffic light to Red\n", end="")
        elif key.char == 'g':
            # light_state = carla.TrafficLightState.Green
            for i in range(30, 33):
                traffic_lights[i].set_state(carla.TrafficLightState.Red)
            traffic_lights[spec_id + 30].set_state(carla.TrafficLightState.Green)
            print("Set Traffic light to Green\n", end="")
    except AttributeError:
        if key == keyboard.Key.tab:
            spec_id += 1
            if spec_id == 3:
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
        elif key == keyboard.Key.esc:
            # Stop listener
            return False

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.load_world('Town01')

settings = world.get_settings()
settings.synchronous_mode = True # Enables synchronous mode
settings.fixed_delta_seconds = 0.05
world.apply_settings(settings)

traffic_lights = world.get_actors().filter("traffic.traffic_light")

spectator = world.get_spectator()
spectator.set_transform(carla.Transform(
    carla.Location(x=83.918785, y=106.423500, z=6.480291), 
    carla.Rotation(pitch=-25.652645, yaw=73.435905, roll=-0.000030)))

print(spectator.get_transform())

print("--------------------------------")
print("| tab : change perspective.    |")
print("|  r  : change light to red.   |")
print("|  g  : change light to green. |")
print("--------------------------------")


for i in range(30, 33):
    traffic_lights[i].set_red_time(1000.0)
    traffic_lights[i].set_green_time(5.0)
    traffic_lights[i].set_yellow_time(0.0)
    traffic_lights[i].set_state(carla.TrafficLightState.Red)


listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

while True:

    print(traffic_lights[30].get_state(), 
          traffic_lights[31].get_state(), 
          traffic_lights[32].get_state())
    
    time.sleep(0.1)
    world.tick()
