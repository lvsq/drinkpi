#Op Codes for tini-server communication
OPCODE_SERVER_LOGIN = '0'
OPCODE_SERVER_DROP_ACK = '4'
OPCODE_SERVER_DROP_NACK = '5'
OPCODE_SERVER_SLOT_STATUS = '7'
OPCODE_SERVER_TEMPERATURE = '8'
OPCODE_SERVER_NOOP = '9'

OPCODE_TINI_ERROR = '-1'
OPCODE_TINI_LOGIN_ACK = '1'
OPCODE_TINI_LOGIN_NACK = '2'
OPCODE_TINI_DROP = '3'
OPCODE_TINI_SLOT_STATUS = '6'


HOST = 'austindrinktest.csh.rit.edu'
PORT = 4343
PASSWD = 'password'

import asyncore, socket, time
import threading
import drink
class PIClient(asyncore.dispatcher):

	def __init__(self):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((HOST, PORT))
		self.send(OPCODE_SERVER_LOGIN + ' ' + PASSWD + '\n')
		self.buffer = OPCODE_SERVER_LOGIN + ' ' + PASSWD + '\n'
		self.drinkmachine = drink.drinkMachine()
		self.bufferLock = False
		noopThread = self.noopThread(self)
		noopThread.start()
		
	def handle_connect(self):
		pass

	def handle_close(self):
		self.close()

	def initiate_reconnect_with_server(self):
		print("Attempting to reconnect to server...")
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((HOST, PORT))
		self.send(OPCODE_SERVER_LOGIN + ' ' + PASSWD + '\n')
		self.buffer = OPCODE_SERVER_LOGIN + ' ' + PASSWD + '\n'
		self.drinkmachine = drink.drinkMachine()
		self.bufferLock = False
		noopThread = self.noopThread(self)
		noopThread.start()

	def handle_error(self):
		print("Problem reaching server...")
		self.initiate_reconnect_with_server()

	def commandSwitch(self,receivedBuffer):
		print ("RESERVES ARE LOW, FEED THE NEEDY")
		print (receivedBuffer)
		if OPCODE_TINI_LOGIN_ACK == receivedBuffer[0]:
			print 'ACK!'
		elif OPCODE_TINI_LOGIN_NACK in receivedBuffer[0]:
			print 'NACK!'
		elif OPCODE_TINI_SLOT_STATUS  in receivedBuffer[0]:
			print 'Server wants slot info.'
			self.buffer = self.giveSlotInfo()
			self.handle_write()
		elif OPCODE_TINI_DROP in receivedBuffer[0]:
			print 'Server wants to drop a drink.'
			self.bufferLock = True
			slot = int(receivedBuffer[1:(len(receivedBuffer)-1)])
			success = self.drinkmachine.dropDrink(slot)
			if success == True:
				print('DROP ACK!')
				self.buffer = OPCODE_SERVER_DROP_ACK + '\n'
				self.handle_write()
				self.bufferLock = False
				#self.buffer = self.giveSlotInfo()
				#self.handle_write()
			else:
				print('DROP NACK!')
				self.buffer = OPCODE_SERVER_DROP_NACK + '\n'
				self.handle_write()
				#self.buffer = self.giveSlotInfo()
				#self.handle_write()
				self.bufferLock = False
		else:
			print receivedBuffer

	def handle_read(self):
		buffer = self.recv(8192)
		self.commandSwitch(buffer)
        def writable(self):
		return (len(self.buffer) > 0)

	def handle_write(self):
		print 'writing ' + self.buffer
		sent = self.send(self.buffer)
		self.buffer = self.buffer[sent:]

	def noop(self):
		#Use temp instead of noops because we have a sensor
		temperature = self.drinkmachine.getTemp()
		return (OPCODE_SERVER_TEMPERATURE + ' ' + str(temperature) + '\n')
		#return '9\n'

	def giveSlotInfo(self):
		builderString = '7 '
		statuses = self.drinkmachine.getAllStatus()
		builderString = ''.join([builderString, statuses, ' \n'])
		print builderString
		return builderString

	class noopThread(threading.Thread):
		def __init__(self, piclient):
			threading.Thread.__init__(self)
			self.piclient = piclient
			self.firstrun = True
			self.bufferLock = False
		def run(self):
			while(True):
				if (self.firstrun == True):
					time.sleep(10)
					self.firstrun = False
				print ('noop')
				if self.bufferLock == False:
					self.piclient.buffer = self.piclient.noop()
					self.piclient.handle_write()
					self.piclient.buffer = self.piclient.giveSlotInfo()
					self.piclient.handle_write()
				time.sleep(30)

client = PIClient()
asyncore.loop(120)
