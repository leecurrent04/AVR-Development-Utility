LIBRARYIES = library

compile:
	avr-gcc -Wall -mmcu=None -Os main.c ${LIBRARIES} -o ./.out/output.o
	avr-objcopy -j .text -j .data -O ihex ./.out/output.o ./.out/main.hex

clean:
	rm -f ./.out/*.o ./.out/*.hex
        
	
upload:
	avrdude -v -p @ADU_MCU@ -c @ADU_TOOL@ -P @ADU_PORT@ -b @ADU_BR@ -U flash:w:./.out/main.hex:i
