

bin/main: build/__src_main.o build/__src_app.o 
	c++  -o $@ $^ -lpthread -lpng -ggdb -static 

build/__src_main.o: src/main.cc
	c++ -Ithirdparty/ -lpthread -lpng -ggdb -static -c -o build/__src_main.o ./src/main.cc

build/__src_app.o: src/app.cc src/app.h src/config.h
	c++ -Ithirdparty/ -lpthread -lpng -ggdb -static -c -o build/__src_app.o ./src/app.cc

