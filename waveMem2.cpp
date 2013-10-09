#include <unistd.h>
#include <sys/types.h>
#include <errno.h>
#include <stdio.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <iostream>

using namespace std;

int main(int argc, char *argv[])
{
  pid_t childPID;
  cout << "pid = " << (int)getpid() <<"\n";
  childPID = fork();
  if (childPID >= 0 ) { // fork ok
    if (childPID == 0) {
      cout << "child pid = " << (int)getpid() <<"\n";
      system("./waveMem");
    } else {
      cout << "forked pid = " << (int)getpid() <<"\n";
      system("./waveMem");
    }
  }
  
  return 0;
}


