import asyncio
from aiomqtt import Client
import aiomqtt.exceptions

async def publish_stop_conveyor(host, port):
    try:
        async with Client(hostname=host, port=port, timeout=10) as client:
            await client.publish("conveyor/commands", "stop_conveyor")
            print("Published 'stop_conveyor' message to 'conveyor/commands'")
    except aiomqtt.exceptions.MqttError as e:
        print(f"MQTT Error: {e}")

if __name__ == "__main__":
    asyncio.run(publish_stop_conveyor("127.0.0.1", 1883))
