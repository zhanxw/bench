#include <stdlib.h>
#include <iostream>
int main(int argc, char *argv[])
{
  double k = 1.0;
  for (int i = 0; i < 20000; ++i) {
    for (int j = 0; j < 20000; ++j) {
      if (rand() %2 == 0) {
        k *= (1.0 + i ) / (1.0 + j);
      } else {
        k /= (1.0 + i ) / (1.0 + j);
      }
    }
  }
  return 0;
}
