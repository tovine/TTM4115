from mqtt_client import QOS_0, QOS_1, QOS_2
try:
	import RPi.GPIO as GPIO
except RuntimeError:
	print("Error importing RPi.GPIO. Try running as superuser in a RPi")
	import sys
	sys.exit(1)

sensor_topic = "door/%i/sensor"
state_topic = "door/%i/state"
states = {True:"open", False:"closed"}
DEAD = "dead"
ALIVE = "alive"

#actually a coroutine
def maincoro(eventloop, mqtt, ID, gpio_port):
	mqtt.set_lastwill(sensor_topic % ID, DEAD, QOS_1, retain=True)
	
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(gpio_port, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	
	async def runtime(eventLoop, mqtt, ID, gpio_port):
		await mqtt.publish(sensor_topic%ID, ALIVE, QOS_1, retain=True)
		
		PrevDoorstate = GPIO.input(gpio_port)
		await mqtt.publish(state_topic%ID, states[PrevDoorstate], QOS_1, retain=True)
		
		while 1:
			await asyncio.sleep(1)
			
			Doorstate = GPIO.input(gpio_port)
			
			if PrevDoorstate != Doorstate:
				await mqtt.publish(state_topic%ID, states[Doorstate], QOS_1, retain=True)
				PrevDoorstate = Doorstate
		
		await mqtt.publish(sensor_topic%ID, DEAD, QOS_1, retain=True)
	return runtime(eventloop, mqtt, ID, gpio_port)
