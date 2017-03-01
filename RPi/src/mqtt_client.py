from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2



async def main_coro(broker, port):
	C = MQTTClient()
	await C.connect('mqtt://test.mosquitto.org/')
	await C.subscribe([('$SYS/broker/uptime', QOS_0)])
	
	try:
		while 1:
			message = await C.deliver_message()
			packet = message.publish_packet
			
			print("%s: %s" % (packet.variable_header.topic_name, str(packet.payload.data)))
		
		await C.unsubscribe(['#'])
		await C.disconnect()
		
	except ClientException as ce:
		print("Client exception: %s" % ce)
