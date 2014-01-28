#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

FILE * secure_open(const char* filename)
{
	FILE *fr=fopen(filename,"rw+");
	if(fr==NULL){
		//create if file not exists
		fr=fopen(filename,"w+");
		if(fr==NULL){
			fprintf(stderr,"File %s not open!/n",filename);
			return NULL;
		}
	};
	if(fseek(fr,0L,SEEK_END)!=-1){
			printf("File size:%ld\n",ftell(fr));
	}else
		{
			fprintf(stderr,"File error!/n");
			return NULL;
		}
	return fr;
}


FILE *fidx, *fr;
char s_target[100000];
char s[100000] ;
int binary_search(int begin,int end)
{
	//printf("searching in %d to %d\n",begin,end);
	if (end<=begin) return -1;
	
	//Found.
	memset(s,sizeof(s),0);
	fseek(fidx,begin,0);
	fscanf(fidx,"%[^,]",s);
	if (strcmp(s,s_target)==0) return begin;
		
	if(fseek(fidx,begin,0)!=-1){
		
		int middle = (begin+end)/2;
		fseek(fidx,middle,0);
		fscanf(fidx,"%[^\n]%[\n]",s,s);//jump to next line
		middle = ftell(fidx);
		
		//less than one line
		if (middle == end)
		{
			fseek(fidx,begin,0);
			fscanf(fidx,"%[\n]%[^\n]%[\n]",s,s,s);//jump to next line
			middle = ftell(fidx);
		}
		if (middle >= end) return -2;
		
		//Found.	
		//printf("Middle addres:%d, end address: %d\n",middle,end);
		
		fseek(fidx,middle,0);
		memset(s,sizeof(s),0);
		fscanf(fidx,"%[^,]",s);
		//printf("Middle key:%s\n",s);
		if (strcmp(s,s_target)==0) return middle;
		//Continue;
		if (strcmp(s,s_target)>0)
			return binary_search(begin,middle);
		else
			return binary_search(middle,end);
	}
	return -1;
}

void print(int res)
{
	fseek(fidx,res,0);
	unsigned int from=0;
	fscanf(fidx,"%[^,]%[,]%x",s,s,&from);
	//printf("\n%d~%d",from,to);
	fseek(fr,from,0);
	char Ptr[1000000];
	//char *Ptr = (char *)malloc((to-from+1) * sizeof(char)); 
	//fgets(Ptr, to-from+1, fr);
	fscanf(fr,"{%[^}]",Ptr);
	//printf("\n%s",Ptr);
}
int main()
{
	
	int stime;
	long ltime;
	
	ltime = time(NULL);
	stime = (unsigned) ltime/2;
	srand(stime);
	int starttime = clock();
	
	
	fr=secure_open("../../build/storage/local.object");
	fidx=secure_open("/dev/shm/aos-index.csv");
	int index_size=ftell(fidx);
	
	for (int i=1;i<=100000; i++)
	{
		sprintf(s_target,"人");
		int res=binary_search(0,index_size);
		//printf("\nResult: %d",res);
		//print(res);
	};
	printf("\n%f seconds\n",((float)(clock()-starttime))/CLOCKS_PER_SEC);
	
}
