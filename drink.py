import subprocess
import time

#subprocess.call("echo '1' > /mnt/w1/05.61FF0D000000/PIO", shell=True)
#time.sleep(.5)
#subprocess.call("echo '0' > /mnt/w1/05.61FF0D000000/PIO", shell=True)

class drinkMachine():
	def __init__ (self):
		self.slots = []
		self.sensors = []
		for item in open('config/bigdrink.config'):
			if (item[:2] == '05'):
				self.slots.append(slot(item.rstrip()))
			elif (item[:2] == '28'):
				self.sensors.append(sensor(item.rstrip()))
			
	def getAllStatus(self):
			outstr = ''
			for x in range(0, len(self.slots)):
				status = '0'
				if (self.slots[x].getStatus()):
					status = '1'
				outstr += str((x + 1)) + ' ' + status
				if (x != len(self.slots) - 1):
					outstr += ' ` '
			return outstr

	def dropDrink(self, slotNumber):
		return self.slots[slotNumber - 1].dropDrink()
	
	def getTemp(self):
		if len(self.sensors) > 0:
			#print self.sensors[0]
			return self.sensors[0].getTemp()
		else:
			return -1

	
class slot():
	def __init__ (self, idNumber):
		self.idNumber = idNumber
		self.lock = False

	def getStatus(self):
		try:
			file = open(''.join(['/mnt/w1/',self.idNumber,'/id']))
			print "Slot: " + self.idNumber + " active."
			file.close()
		except IOError as e:
			#print "I/O error({0}): {1}".format(e.errno, e.strerror)	
			print "Slot: " + self.idNumber + " disabled."
			return False
		return True 
	
	def getLock(self):
		return self.lock

	def setLock(self):
		self.lock = True
	
	def setUnlock(self):
		self.lock = False
	
	def dropDrink(self):
		if self.getStatus():
			print "Slot Status: Good"
			if not self.getLock():
				print "Lock Status: Unlocked"
				self.setLock()
				try: 
					subprocess.call("".join(["echo '1' > /mnt/w1/", self.idNumber,"/PIO"]), shell=True)
					time.sleep(.5)
					subprocess.call("".join(["echo '0' > /mnt/w1/", self.idNumber,"/PIO"]), shell=True)
				except IOError:
					print ('shit keeps breaking because it is shit.')
				time.sleep(2)
				self.setUnlock()
				return True
		return False

class sensor():
	def __init__ (self, idNumber):
		self.idNumber = idNumber
	
	def getStatus(self):
		try:
			file = open(''.join(['/mnt/w1/', self.idNumber, '/id']))
			file.close()
		except IOError:
			return False
		return True

	def getTemp(self):
		try:
			tempFile = open(''.join(['/mnt/w1/', self.idNumber, '/temperature12']))
			text = tempFile.read()
			tempFile.close()
			#celsius from the onewire
			temperature = text.strip()
			print "Celsius is: " + temperature
			f_temperature = float(temperature) * (9.0/5) + 32
			print "Farenheight is " + str(f_temperature)
			#print temperature
			#temperature = (float(text.split('\n')[1].split(' ')[9][2:]) / 1000) * (9/5) + 32
		except IOError:
			return -1
		#print temperature
		return f_temperature

if __name__ == '__main__':
	drinkmachine = drinkMachine()
	print (drinkmachine.getAllStatus())
	

