#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

int main(int argc, char** argv) {
  int mem = 0;
  if (argc >= 2) {
    mem = atoi(argv[1]);
  }
  int dtime = 10;
  if (argc >= 3) {
    dtime = atoi(argv[2]);
  }

  fprintf(stderr, "Consume %d k memory and sleep %d seconds\n", mem, dtime);
  time_t t0 = time(NULL);
  time_t t1;

  char* p = new char[mem * 1024];
  while(true)  {
    for (int i = 0; i < mem * 1024; ++i) {
      p[i] = (p[i] + p[i] * i) % 2;
    }
    t1 = time(NULL);
    if (abs(difftime(t0, t1)) > dtime)
      break;
  }

  return 0;
}
