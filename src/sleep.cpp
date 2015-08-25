#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char** argv) {
  int mem = 0;
  if (argc >= 2) {
    mem = atoi(argv[1]);
  }
  int time = 10;
  if (argc >= 3) {
    time = atoi(argv[2]);
  }

  fprintf(stderr, "Consume %d k memory and sleep %d seconds\n", mem, time);
  char* p = new char[mem * 1024];
  sleep(time);
  for (int i = 0; i < mem * 1024; ++i) {
    p[i] = (p[i] + p[i] * i) % 2;
  }
  
  return 0;
}
