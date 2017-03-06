import asyncio
from inspect import iscoroutinefunction
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2

class MQTT():
	config = {
		'auto_reconnect': True,
		'reconnect_max_interval': 5,
		'reconnect_retries': 30
	}
	
	def __init__(self, EventLoop, broker, port=1883, use_ssl=False):
		assert type(use_ssl) is bool
		assert type(port) is int
		
		self.EventLoop = EventLoop
		self.C = MQTTClient(config=self.config)#, loop=EventLoop)
		self.broker = 'mqtt%s://%s:%i/' % ("s"*use_ssl, broker, port)
				
		#keeping track of subscrptions:
		self.topic = {}#["topic"] = [callback]
		self.connected = False
		
		self.queue = []#deasyncify. [i] = (func, args, kwargs)
	
	#async methods
	async def publish(self, topic, data, qos=None):
		while not self.connected:
			await asyncio.sleep(0.2)
		
		if type(data) != bytes:
			data = bytes(data, "UTF-8")
		
		await self.C.publish(topic, data, qos=qos)
	async def subscribe(self, topic, callback=lambda data: None, decode=True, qos=QOS_0):#no wildchar support
		while not self.connected:
			await asyncio.sleep(0.2)
		
		if decode:
			old = callback
			def callback(data):
				old(str(data, "utf-8"))
		
		self.topic[topic] = callback
		await self.C.subscribe([(topic, qos)])
			
	#normal methods (requires queue_coro to be running as well)
	def enqueue_publish(self, *args, **kwargs):
		self.queue.append((self.publish, args, kwargs))
	def enqueue_subscribe(self, *args, **kwargs):
		self.queue.append((self.subscribe, args, kwargs))
	
	#mainloops
	async def main_coro(self, debug=False, stopLoop=False):
		C = self.C
		
		if debug: print("Connecting to %s..." % self.broker)
		
		await C.connect(self.broker)
		self.connected = True
		
		if debug:print("Connected to %s" % self.broker)
		
		try:
			while 1:
				message = await C.deliver_message()
				packet = message.publish_packet
				if debug:
					print("%s: %s" % (packet.variable_header.topic_name, str(packet.payload.data, "utf-8")))
				
				if packet.variable_header.topic_name in self.topic:
					func = self.topic[packet.variable_header.topic_name]
					self.EventLoop.call_soon(func, packet.payload.data)
				
			await C.unsubscribe(list(self.topic.keys()))
			await C.disconnect()
			
			if debug:print("Disconnected from %s" % self.broker)
		except ClientException as ce:
			print("Client exception: %s" % ce)

		self.connected = False
		
		if stopLoop:
			self.EventLoop.stop()
	
	async def queue_coro(self):#optional loop
		while 1:
			while self.queue:
				func, args, kwargs = self.queue.pop(0)
				await func(*args, **kwargs)
			await asyncio.sleep(1)
	


