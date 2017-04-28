from mqtt_client import QOS_0, QOS_1, QOS_2
try:
	import RPi.GPIO as GPIO
except RuntimeError:
	print("Error importing RPi.GPIO. Try running as superuser in a RPi")
	import sys
	sys.exit(1)


sensor_topic = "door/%s/sensor"
state_topic = "door/%s/state"
states = {True:"open", False:"closed"}
DEAD = "dead"
ALIVE = "alive"


#actually a coroutine
def maincoro(eventloop, mqtt, ID, gpio_port):
	print("maincoro start")
	mqtt.set_lastwill(sensor_topic % ID, DEAD, QOS_1, retain=True)
	
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(gpio_port, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	
	@asyncio.coroutine
	def runtime(eventLoop, mqtt, ID, gpio_port):
		print("runtime start")
		yield from mqtt.publish(sensor_topic%ID, ALIVE, QOS_1, retain=True)
		
		PrevDoorstate = GPIO.input(gpio_port)
		yield from mqtt.publish(state_topic%ID, states[PrevDoorstate], QOS_1, retain=True)
		
		print("runtime loop start")
		while 1:
			yield from asyncio.sleep(1)
			
			print("gpio input")
			Doorstate = GPIO.input(gpio_port)
			
			
			if PrevDoorstate != Doorstate:
				print("publish ")
				yield from mqtt.publish(state_topic%ID, states[bool(Doorstate)], QOS_1, retain=True)
				PrevDoorstate = Doorstate
		
		yield from mqtt.publish(sensor_topic%ID, DEAD, QOS_1, retain=True)
	return runtime(eventloop, mqtt, ID, gpio_port)
