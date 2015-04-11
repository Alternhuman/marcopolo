// Ejemplo MPI_Type_contiguous

# define TAMCADENA 100
# include "mpi.h"
# include <stdio.h>
# include <math.h>

#define NUM	4

int main (int argc , char **argv) {
	int iId ; 
	int iNumProcs;
	int i,j; 
	double tmpInic = 0.0; 
	double tmpFin; 
	
	double S[NUM][NUM];
	double R[NUM];

	MPI_Status status;
	MPI_Datatype	tipo_S;
	MPI_Datatype	tipo_R;

	MPI_Init (&argc ,&argv); 						
	MPI_Comm_rank(MPI_COMM_WORLD,&iId ); 			
	MPI_Comm_size(MPI_COMM_WORLD, & iNumProcs ); 	
	
	MPI_Type_vector(NUM, 1, NUM+1, MPI_DOUBLE, &tipo_S);
	MPI_Type_commit(&tipo_S);
	MPI_Type_vector(NUM, 1, 1, MPI_DOUBLE, &tipo_R);
	MPI_Type_commit(&tipo_R);	
	
	for (i=0; i<NUM;i++) 
		for (j=0; j<NUM; j++)
			S[i][j]=0;
	
	if (iId==0)
	{
		for (i=0; i<NUM;i++) 
		{	
			for (j=0; j<NUM; j++)
			{
				S[i][j]=i*NUM+j;
				printf("%.2f ",S[i][j]);
			}
			printf("\n");
		}
		MPI_Send(S,1,tipo_S,1,10,MPI_COMM_WORLD);	
	}
	else
	{
		MPI_Recv(R,1,tipo_R,0,10,MPI_COMM_WORLD,&status);	

		for (i=0; i<NUM;i++) 
		{	
				printf("%.2f ",R[i]);
			  printf("\n");
		}		
	
	}
	
	if (iId==0) { 
		fprintf(stdout, "Numero Procesos: %d \n" , iNumProcs) ;
	}
	MPI_Finalize(); 
	return 0 ;
}
