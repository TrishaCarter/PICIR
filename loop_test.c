#include <stdio.h>

int main() {
    int i, sum = 0;
    
    for (i = 0; i < 10; i++) {
        sum += i;
    }
    
    for (int j = 0; j < 5; j++) {
        printf("%d\n", j);
    }
    
    printf("Sum: %d\n", sum);
    return 0;
}

