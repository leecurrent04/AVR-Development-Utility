OBJ_FILES=%s

compile:
	@echo "" && date
	
	avr-gcc -Wall -mmcu=%s -Os main.c ${OBJ_FILES} -o ./.out/output.o
	avr-objcopy -j .text -j .data -O ihex ./.out/output.o ./.out/main.hex
	
	@echo "\\n========================================\\n"
	@avr-size -C --mcu=%s ./.out/output.o

clean:
	rm -f ./.out/*.o ./.out/*.hex


%s
