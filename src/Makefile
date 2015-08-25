all: burn sleep burn.burn burn.sleep
	g++ -o waveMem waveMem.cpp
	g++ -o waveMem2 waveMem2.cpp
	g++ -o burnCpu burnCpu.cpp
burn: burn.cpp
	g++ -o burn burn.cpp -O2
sleep: sleep.cpp
	g++ -o sleep sleep.cpp -O2
burn.burn: burn.burn.cpp
	g++ -o burn.burn burn.burn.cpp -O2
burn.sleep: burn.sleep.cpp
	g++ -o burn.sleep burn.sleep.cpp -O2
clean:
	rm -f waveMem waveMem2 burnCpu
	rm -f burn sleep burn.burn burn.sleep
