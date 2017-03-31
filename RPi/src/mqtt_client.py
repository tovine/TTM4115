import asyncio
from inspect import iscoroutinefunction
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2
from hbmqtt.broker import Broker

def matches(topic, a_filter):
	return Broker.matches(none, topic, a_filter)

class MQTT():
	config = {
		'auto_reconnect': True,
		'reconnect_max_interval': 5,
		'reconnect_retries': 30
	}
	
	def __init__(self, EventLoop, broker, port=1883, use_ssl=False):
		assert type(use_ssl) is bool
		assert type(port) is int
		self.config = self.config.copy()
		
		self.EventLoop = EventLoop
		self.C = MQTTClient(config=self.config)#, loop=EventLoop)
		self.broker = 'mqtt%s://%s:%i/' % ("s"*use_ssl, broker, port)
		self.lastwill = None
		
		#keeping track of subscrptions:
		self.topics = {}#["topic"] = [callback]
		self.connected = False
		
		self.queue = []#deasyncify. [i] = (func, args, kwargs)
	
	#further config
	def set_lastwill(self, topic, message, QOS, retain = False):#must set be done before main_coro is run
		self.config["will"] = {
			"message": message,
			"topic": topic,
			"qos": QOS,
			"retain" : retain
		}
		self.C.config.update(self.config)#totally not a bodge
	
	#coroutines
	async def publish(self, topic, data, qos=None):
		while not self.connected:
			await asyncio.sleep(0.2)
		
		if type(data) != bytes:
			data = bytes(data, "UTF-8")
		
		await self.C.publish(topic, data, qos=qos)
	async def subscribe(self, topic, callback=lambda topic, data: None, decode=True, qos=QOS_0):
		while not self.connected:
			await asyncio.sleep(0.2)
		
		if decode:
			old = callback
			def callback(topic, data):
				old(topic, (str(data, "utf-8"))
		
		self.topics[topic] = callback
		await self.C.subscribe([(topic, qos)])
		
	#normal counterparts (requires queue_coro() to be running alongside main_coro())
	def enqueue_publish(self, *args, **kwargs):
		self.queue.append((self.publish, args, kwargs))
	def enqueue_subscribe(self, *args, **kwargs):
		self.queue.append((self.subscribe, args, kwargs))
	
	#mainloop
	async def main_coro(self, debug=False, stopLoop=False):
		C = self.C
		
		if debug: print("Connecting to %s..." % self.broker)
		
		await C.connect(self.broker)
		self.connected = True
		
		if debug: print( "Connected to %s" % self.broker)
		
		asyncio.ensure_future(self._queue_coro())
		#await self.EventLoop.create_task(cor1())
		
		try:
			while 1:
				message = await C.deliver_message()
				topic = message.publish_packet.variable_header.topic_name
				data = message.publish_packet.payload.data
				if debug:
					print("%s: %s" % (topic, str(data, "utf-8")))
				
				for func in (self.topics[i] for i in self.topics if matches()):
					self.EventLoop.call_soon(func, data)
			
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
	


