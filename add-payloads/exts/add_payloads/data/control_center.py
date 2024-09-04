from paho.mqtt import client as mqtt_client

def start_mqtt_client(host, port, db):
    def on_message(client, userdata, message):
        payload = message.payload.decode()
        if payload == "stop_conveyor":
            db.per_instance_state.stop_conveyor_flag = True
        elif payload == "activate_conveyor":
            db.per_instance_state.activate_conveyor_flag = True

    client = mqtt_client.Client()
    client.on_message = on_message
    client.connect(host, port)
    client.subscribe("conveyor/commands")
    client.loop_start()
    return client

def setup(db: og.Database):
    state = db.per_instance_state

    state.mqtt_flag = False
    state.mqtt_client = None
    
    state.stop_conveyor_flag = False
    state.activate_conveyor_flag = False

    # Initialize MQTT client
    state.mqtt_host = '127.0.0.1'  # Set your MQTT broker host
    state.mqtt_port = 1883  # Set your MQTT broker port

def cleanup(db: og.Database):
    if db.per_instance_state.mqtt_client:
        db.per_instance_state.mqtt_client.loop_stop()
        db.per_instance_state.mqtt_client.disconnect()

def compute(db: og.Database):
    state = db.per_instance_state

    if not state.mqtt_flag:
        state.mqtt_flag = True
        state.mqtt_client = start_mqtt_client(state.mqtt_host, state.mqtt_port, db)

    if state.stop_conveyor_flag:
        db.outputs.is_stop = True
        state.stop_conveyor_flag = False
    else:
        db.outputs.is_stop = False

    if state.activate_conveyor_flag:
        db.outputs.is_activate = True
        state.activate_conveyor_flag = False
    else:
        db.outputs.is_activate = False

    return True

