"""
Apple Imagewriter
"""

from serial import Serial, SEVENBITS, PARITY_NONE, STOPBITS_ONE, serialutil
from time import sleep
from logging import basicConfig, DEBUG, StreamHandler, getLogger

basicConfig(
    level=DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        StreamHandler()
    ]
)

class AppleImageWriter():
	def __init__(self, serialPort: str, baudRate=9600, useDTR=True, useXONXOFF=False, pollTime=1) -> None:
		if (not str): raise AttributeError("serialPort must be provided.")
		if (useDTR and useXONXOFF): raise AttributeError("Only one protocol allowed. (DTR or XON/XOFF)")
		if (not useDTR and not useXONXOFF): raise AttributeError("One protocol must be enabled. (DTR or XON/XOFF)")

		self.logger     = getLogger("AppleImageWriter")
		self.serialPort = serialPort
		self.baudRate   = baudRate
		self.useDTR     = useDTR
		self.useXONXOFF = useXONXOFF
		self.pollTime   = pollTime
		self.inUse      = False
	
	def connect(self) -> None:
		try:
			self.printer = Serial(
				port=self.serialPort,
				baudrate=self.baudRate,
				bytesize=SEVENBITS,
				parity=PARITY_NONE,
				stopbits=STOPBITS_ONE,
				xonxoff=self.useXONXOFF,
				dsrdtr=self.useDTR
			)
		except serialutil.SerialException as err:
			self.logger.error(f"Cannot connect to ImageWriter. Error: ${err}")
	
	def disconnect(self) -> None:
		if self.printer:
			self.printer.close()
			self.printer = None

	async def print(self, ascii: str ) -> None:
		if self.inUse:
			self.logger.warning("Printer already in use. Try again later.")
			raise RuntimeError("Printer already in use. Try again later.")

		self.inUse = True
		self.printer.write(b"\x11") # Send DC1

		running = True
		for char in ascii:
			busy = not self.printer.dtr
			while busy:
				sleep(self.pollTime)
				busy = not self.printer.dtr

			self.printer.write(bytes(char))
		
		self.inUse = False
	
	@property
	def underline(self):
		return self._underline

	@underline.setter
	def underline(self, value: bool) -> None:
		self._underline = value

		command: str
		if value:
			command = b"\x27\x88"
		else:
			command = b"\x27\x89"
		self.printer.write(command)

	@property
	def boldface(self):
		return self._boldface

	@boldface.setter
	def boldface(self, value: bool) -> None:
		self._boldface = value

		command: str
		if value:
			command = b"\x27\x33"
		else:
			command = b"\x27\x34"
		self.printer.write(command)
	
	@property
	def headline(self):
		return self._headline
	
	@headline.setter
	def headline(self, value: bool) -> None:
		self._headline = value

		command: str
		if value:
			command = b"\x14"
		else:
			command = b"\x15"
		self.printer.write(command)

	def softwareReset(self) -> None:
		if self.printer:
			self.printer.write(b"\x11") # Send DC1
			self.printer.write(b"\x27\x99")
