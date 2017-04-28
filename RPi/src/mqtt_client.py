import asyncio
#from inspect import iscoroutinefunction
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2
from hbmqtt.broker import Broker

def matches(topic, a_filter):
	return Broker.matches(None, topic, a_filter)

class MQTT():
	config = {
		'auto_reconnect': True,
		'reconnect_max_interval': 5,
		'reconnect_retries': 30
	}
	
	def __init__(self, EventLoop, broker):
		self.config = self.config.copy()
		
		self.EventLoop = EventLoop
		self.C = MQTTClient(config=self.config)#, loop=EventLoop)
		self.broker = broker
		self.lastwill = None
		self.cafile=None
		
		#keeping track of subscriptions:
		self.topics = {}#["topic"] = [callback]
		self.connected = False
		
		self.queue = []#deasyncify. [i] = (func, args, kwargs)
	
	#further config
	def set_lastwill(self, topic, message, QOS, retain = False):#must set be done before main_coro is run
		self.config["will"] = {
			"message": bytes(message, "UTF-8"),
			"topic": topic,
			"qos": QOS,
			"retain" : retain
		}
		self.C.config.update(self.config)#totally not a bodge
	def set_certfile(self, cafile):#must set be done before main_coro is run
		self.cafile = cafile
	#coroutines
	@asyncio.coroutine
	def publish(self, topic, data, qos=None, retain=False):
		while not self.connected:
			yield from asyncio.sleep(0.2)
		
		if type(data) != bytes:
			data = bytes(data, "UTF-8")
		
		yield from self.C.publish(topic, data, qos=qos, retain=retain)
	@asyncio.coroutine
	def subscribe(self, topic, callback=lambda topic, data: None, decode=True, qos=QOS_0):
		while not self.connected:
			yield from asyncio.sleep(0.2)
		
		if decode:
			old = callback
			def callback(topic, data):
				old(topic, (str(data, "utf-8")))
		
		self.topics[topic] = callback
		yield from self.C.subscribe([(topic, qos)])
		
	#normal counterparts
	def enqueue_publish(self, *args, **kwargs):
		self.queue.append((self.publish, args, kwargs))
	def enqueue_subscribe(self, *args, **kwargs):
		self.queue.append((self.subscribe, args, kwargs))
	
	#mainloop
	@asyncio.coroutine
	def main_coro(self, debug=False, stopLoop=False):
		C = self.C
		
		if debug: print("Connecting to %s..." % self.broker)
		
		yield from C.connect(self.broker, cafile=self.cafile)
		self.connected = True
		
		if debug: print( "Connected to %s" % self.broker)
		
		asyncio.ensure_future(self._queue_coro())
		
		try:
			while 1:
				message = yield from C.deliver_message()
				topic = message.publish_packet.variable_header.topic_name
				data = message.publish_packet.payload.data
				if debug:
					print("%s: %s" % (topic, str(data, "utf-8")))
				
				for func in (self.topics[i] for i in self.topics if matches(topic, i)):
					self.EventLoop.call_soon(func, topic, data)
			
			yield from C.unsubscribe(list(self.topic.keys()))
			yield from C.disconnect()
			
			if debug:print("Disconnected from %s" % self.broker)
		except ClientException as ce:
			print("Client exception: %s" % ce)

		self.connected = False
		
		if stopLoop:
			self.EventLoop.stop()
	@asyncio.coroutine
	def _queue_coro(self):
		while 1:
			while self.queue:
				func, args, kwargs = self.queue.pop(0)
				yield from func(*args, **kwargs)
			yield from asyncio.sleep(1)
	


