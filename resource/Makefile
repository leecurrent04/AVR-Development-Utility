MCU=@{ADU_MCU}
PORT=@{ADU_PORT}
OBJ_FILES=@{ADU_OBJ_FILES}
BAUDRATE=@{ADU_BAUDRATE}
PROGRAMMER=@{ADU_PROGRAMMER}

compile:
	avr-gcc -Wall -mmcu=${MCU} -Os main.c ${OBJ_FILES} -o ./out/output.o

	avr-objcopy -j .text -j .data -O ihex ./out/output.o ./out/main.hex

upload:
	avrdude -v -p ${MCU} -c ${PROGRAMMER} -P ${PORT} -b ${BAUDRATE} -U flash:w:./out/main.hex:i


clean:
	rm -f ./out/*.o ./out/*.hex
