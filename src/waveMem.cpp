#include <unistd.h>
#include <iostream>
using namespace std;

int main(int argc, char *argv[])
{
  cout << "begin\n";
  char* a = new char[1024*1024*500];
  cout << "allocate 500M\n";
  sleep(2);
  char* b = new char[1024*1024*500];
  cout << "allocate 1,000M\n";
  sleep(4);
  delete[] a;
  cout << "deallocate 500M\n";
  sleep(2);
  return 0;
}


