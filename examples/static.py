from package.main import AppleImageWriter

if __name__ == "__main__":
	# can get serialPort via `ls /dev/tty.*`
	imageWriter = AppleImageWriter(serialPort="")
	imageWriter.connect()

	try:
			imageWriter.print("Here's to the crazy ones. The misfits. The rebels. The troublemakers. The round pegs in the square holes. The ones who see things differently.")
	finally:
		imageWriter.disconnect()
