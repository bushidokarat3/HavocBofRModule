BOFNAME := patchit
CC_x64 := x86_64-w64-mingw32-gcc
CC_x86 := i686-w64-mingw32-gcc

all: x64 x86

x64:
	$(CC_x64) -o ./dist/$(BOFNAME).x64.o -c patchit.c -masm=intel

x86:
	$(CC_x86) -o ./dist/$(BOFNAME).x86.o -c patchit.c -masm=intel

clean:
	rm -f ./dist/$(BOFNAME).x64.o ./dist/$(BOFNAME).x86.o
