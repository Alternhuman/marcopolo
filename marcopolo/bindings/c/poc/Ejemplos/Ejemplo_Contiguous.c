// Ejemplo MPI_Type_contiguous

# define TAMCADENA 100
# include "mpi.h"
# include <stdio.h>

int main (int argc , char **argv) {
	int iId ; 
	int iNumProcs;
	int i; 
	double tmpInic = 0.0; 
	double tmpFin; 
	double Reales[100];
	MPI_Datatype ContiguousReal100;
	MPI_Status status;

	MPI_Init (&argc ,&argv); 						
	MPI_Comm_rank(MPI_COMM_WORLD,&iId ); 			
	MPI_Comm_size(MPI_COMM_WORLD, & iNumProcs ); 	
	
	MPI_Type_contiguous(100, MPI_DOUBLE, &ContiguousReal100);
	MPI_Type_commit(&ContiguousReal100);
		
	if (iId==0)
	{
		for (i=0; i<100;i++) Reales[i]=i*2;
		MPI_Send(Reales,1,ContiguousReal100,1,10,MPI_COMM_WORLD);	
	}
	else
	{
		MPI_Recv(Reales,1,ContiguousReal100,0,10,MPI_COMM_WORLD,&status);	
		for (i=0;i<100;i++) printf("%d) %f\n",i,Reales[i]);
	}
	
	if (iId==0) { 
		fprintf(stdout, "Numero Procesos: %d \n" , iNumProcs) ;
	}
	MPI_Finalize(); 
	return 0 ;
}
