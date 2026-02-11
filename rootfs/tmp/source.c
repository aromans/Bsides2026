#include <stdio.h>
#include <stdlib.h>

void cant_touch_this() {
		
}

int main(int argc, char*argv[]) {
	char value[100];
	FILE *fp = fopen("important.txt", "r");
	if (fp == NULL) { return 1; }
	fscanf(fp, "%s", value); 
    	printf("Content: %s\n", value);
    	fclose(fp);
	return 0;
}
