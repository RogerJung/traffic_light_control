import carla
from pynput import keyboard

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
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

traffic_lights[light_id].set_red_time(5.0)
traffic_lights[light_id].set_green_time(5.0)
traffic_lights[light_id].set_yellow_time(2.0)

while True:

    with keyboard.Events() as events:
        # Block at most one second
        event = events.get(1.0)
        if event is None:
            pass
        else:
            try:
                if type(event) == keyboard.Events.Release:
                    print(' \r', end="")
                    if event.key.char == 'r':
                        if traffic_lights[light_id].get_state() == carla.TrafficLightState.Green:
                            traffic_lights[light_id].set_state(carla.TrafficLightState.Red)
                        print("Set Traffic light to Red\n", end="")
                    elif event.key.char == 'g':
                        if traffic_lights[light_id].get_state() == carla.TrafficLightState.Red:
                            traffic_lights[light_id].set_state(carla.TrafficLightState.Green)
                        print("Set Traffic light to Green\n", end="")
            except AttributeError:
                pass

