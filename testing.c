

int main(int argc, char** argv){

    if (argc < 2){
        return 10 * 3 - 2;
    }

    int c = 2;
    return c;

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


