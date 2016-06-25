PLATFORM=ecv34
PORT=/dev/ttyUSB1

all:
	scons platform=$(PLATFORM)

flash: upload
upload:
	scons platform=ecv34 port=$(PORT) upload

clean:
	rm -rf ./build
