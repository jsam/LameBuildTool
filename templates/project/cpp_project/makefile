

bin/main: build/__src_main.o 
	c++  -o $@ $^ -lpthread -lpng -ggdb -static 

build/__src_main.o: src/main.cc
	c++ -Ithirdparty/ -lpthread -lpng -ggdb -static -c -o build/__src_main.o ./src/main.cc

