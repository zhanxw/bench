#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/types.h>
#include <sys/wait.h>

void burn(int mem, int dtime) {
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
  fprintf(stderr, "Done - mem = %d, dtime = %d, pid = %d\n", mem, dtime, getpid());
}

void sleep(int mem, int dtime) {
  char* p = new char[mem * 1024];
    for (int i = 0; i < mem * 1024; ++i) {
      p[i] = (p[i] + p[i] * i) % 2;
    }
    sleep(dtime);
  fprintf(stderr, "Done - mem = %d, dtime = %d, pid = %d\n", mem, dtime, getpid());
}

int main(int argc, char** argv) {
  int mem = 0;
  if (argc >= 2) {
    mem = atoi(argv[1]);
  }
  int dtime = 10;
  if (argc >= 3) {
    dtime = atoi(argv[2]);
  }

  fprintf(stderr, "First fork()\n");
  fprintf(stderr, "Parent: Consume %d k memory and burn %d seconds\n", mem, dtime);
  fprintf(stderr, "Child: Consume %d k memory and sleep %d seconds\n", mem, dtime);

  pid_t pid = fork();
  if (pid != 0)  { // parent
    burn(mem, dtime);
  } else {
    sleep(mem, dtime);
  }

  wait(0);

  return 0;
}
