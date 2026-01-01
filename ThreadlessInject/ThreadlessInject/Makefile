BOFNAME := threadless-inject
CC_x64 := x86_64-w64-mingw32-gcc
STRIP_x64 := x86_64-w64-mingw32-strip

# Note: This BOF is x64-only due to x64-specific PEB access and shellcode loader

all: x64

x64:
	$(CC_x64) -o dist/$(BOFNAME).x64.o -c entry.c -masm=intel -Wall
	$(STRIP_x64) --strip-unneeded dist/$(BOFNAME).x64.o

clean:
	rm -f dist/$(BOFNAME).x64.o
