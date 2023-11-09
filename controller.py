import carla
from pynput import keyboard
import time


light_state = carla.TrafficLightState.Red

def on_press(key):
    try:
        pass
    except AttributeError:
        pass

def on_release(key):
    global light_state
    try:
        print(' \r', end="")
        if key.char == 'r':
            light_state = carla.TrafficLightState.Red
            print("Set Traffic light to Red\n", end="")
        elif key.char == 'g':
            light_state = carla.TrafficLightState.Green
            print("Set Traffic light to Green\n", end="")
    except AttributeError:
        if key == keyboard.Key.esc:
            # Stop listener
            return False

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

settings = world.get_settings()
settings.synchronous_mode = True # Enables synchronous mode
settings.fixed_delta_seconds = 0.05
world.apply_settings(settings)

light_manager = world.get_lightmanager()
lights = light_manager.get_all_lights()

traffic_lights = []

tmp_map = world.get_map()
for landmark in tmp_map.get_all_landmarks_of_type('1000001'):
    traffic_light = world.get_traffic_light(landmark)
    if traffic_light:
        traffic_lights.append(traffic_light)

light_id = 10

spectator = world.get_spectator()
spectator.set_transform(carla.Transform(traffic_lights[light_id].get_location() + carla.Location(x=10) + carla.Location(y=7) + carla.Location(z=6),
carla.Rotation(pitch=-20, yaw = 180)))

print("------------------------------")
print("| r : change light to red.   |")
print("| g : change light to green. |")
print("------------------------------")

# traffic_lights[light_id].set_red_time(5.0)
traffic_lights[light_id].set_green_time(5.0)
traffic_lights[light_id].set_yellow_time(2.0)

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

while True:
    traffic_lights[light_id].set_state(light_state)
    time.sleep(0.5)
    world.tick()
