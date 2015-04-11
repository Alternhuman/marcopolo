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

	MPI_Status status;
	MPI_Datatype	tipo_vector;

	MPI_Init (&argc ,&argv); 						
	MPI_Comm_rank(MPI_COMM_WORLD,&iId ); 			
	MPI_Comm_size(MPI_COMM_WORLD, & iNumProcs ); 	
	
	MPI_Type_vector(NUM, 1, NUM, MPI_DOUBLE, &tipo_vector);
	MPI_Type_commit(&tipo_vector);
	
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
		MPI_Send(S,1,tipo_vector,1,10,MPI_COMM_WORLD);	
	}
	else
	{
		MPI_Recv(S,1,tipo_vector,0,10,MPI_COMM_WORLD,&status);	
		
		for (i=0; i<NUM;i++) 
		{	
			for (j=0; j<NUM; j++)
			{
	
				printf("%.2f ",S[i][j]);
			}
			printf("\n");
		}
	}
	
	if (iId==0) { 
		fprintf(stdout, "Numero Procesos: %d \n" , iNumProcs) ;
	}
	MPI_Finalize(); 
	return 0 ;
}
