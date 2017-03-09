from mqtt_client import QOS_0, QOS_1, QOS_2
# We could either use https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/
# Or just use the raspbian-included binary /usr/bin/gpio
'''
Example: 
def gpio(cmd, pin, value):
	return subprocess.check_output(["gpio", cmd, str(pin), value])

# Read
gpio("read", pin, None)

# Write
gpio("write", pin, value)
'''
# The disadvantage of calling the binary is that you don't get to subscribe to events on the pins, but have to poll (not really that big a problem though)
