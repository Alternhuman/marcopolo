// Ejemplo 2: MPI_Send , MPI_Recv. Suma Números

# define TAMCADENA 100
# include "mpi.h"
# include <stdio.h>
#include <math.h>

void Obten_Nombre_Procesos(int id, int numprocs)
{
	char nombreproc [MPI_MAX_PROCESSOR_NAME];	
	int lnombreproc; 	
	int etiqueta=50;
	MPI_Status status;
	int origen;

	MPI_Get_processor_name(nombreproc,& lnombreproc);
	
	if (id==0)
	{
		fprintf(stdout,"Proceso %d en %s\n", id, nombreproc);
		
		for (origen=1; origen<numprocs;origen++)
		{
			MPI_Recv(nombreproc,MPI_MAX_PROCESSOR_NAME, MPI_CHAR, origen, etiqueta, MPI_COMM_WORLD, &status);
			fprintf(stdout,"Proceso %d en %s\n", origen, nombreproc);
		}
	}
	else
	{
		MPI_Send(nombreproc, MPI_MAX_PROCESSOR_NAME, MPI_CHAR, 0, etiqueta, MPI_COMM_WORLD);
	}
}

#define NMAX  100 // Desde el id0 podía ser dato de entrada
unsigned long Obten_Dato_Maximo()
{
	return NMAX;
}

unsigned long Suma(unsigned long iInicial, unsigned long iFinal)
{
	unsigned long l;
	unsigned long ulSuma=0L;
	long i;
	double raiz;
	
	for (l=iInicial; l<=iFinal; l++)
	{
		ulSuma+=l;
		//usleep(100000);
		for (i=1; i<33333333; i++)
			raiz=sqrt(i);
	}
	
	return ulSuma;
}

int main (int argc , char **argv) {
	int iId ; 
	int iNumProcs; 
	
	double tmpInic = 0.0; 
	double tmpFin; 
	
	unsigned long ulValorMaximo;
	unsigned long ulSuma=0L;
	unsigned long ulSumaTotal=0L;
	unsigned long ulIntervalo=0L;
	
	int i;
	int iEtiqueta;
	MPI_Status status;

	MPI_Init (&argc ,&argv); 						
	MPI_Comm_rank(MPI_COMM_WORLD,&iId ); 			
	MPI_Comm_size(MPI_COMM_WORLD, & iNumProcs ); 	
	
	// Para saber donde se ejecuta cada cosa
	Obten_Nombre_Procesos(iId, iNumProcs);
	
	// El id=0 mmaneja todas las E/S
	if (iId==0) ulValorMaximo=Obten_Dato_Maximo();
	tmpInic=MPI_Wtime(); 
	// Manda/Recibe los rangos a los diferentes procesos
	if (iId==0)
	{
		ulIntervalo=ulValorMaximo/iNumProcs;
		iEtiqueta=15;		
		// Prodria enviarse con Broadcast, pero es un ejemplo
		for (i=1;i<iNumProcs;i++)
			MPI_Send(&ulIntervalo, 1, MPI_UNSIGNED_LONG, i, iEtiqueta, MPI_COMM_WORLD);
	}
	else
	{
		iEtiqueta=15;
		MPI_Recv(&ulIntervalo,1, MPI_UNSIGNED_LONG, 0, iEtiqueta, MPI_COMM_WORLD, &status);	
	} 
	// Realizan los calculos
	ulSuma=Suma(iId*ulIntervalo+1, iId*ulIntervalo+ulIntervalo);
	// Recibe/Manda resultados
	if (iId==0)
	{
		ulSumaTotal+=ulSuma;
		iEtiqueta=16;	
		fprintf(stdout,"Nodo %d: %ld\n",iId,ulSuma);	
		
		for (i=1; i<iNumProcs; i++)
		{
			MPI_Recv(&ulSuma,1, MPI_UNSIGNED_LONG, i, iEtiqueta, MPI_COMM_WORLD, &status);
			ulSumaTotal+=ulSuma;
			fprintf(stdout,"Nodo %d: %ld\n",i,ulSuma);	
		}
	}
	else
	{
		iEtiqueta=16;	
		MPI_Send(&ulSuma, 1, MPI_UNSIGNED_LONG, 0, iEtiqueta, MPI_COMM_WORLD);
	}
	tmpFin =MPI_Wtime(); 	
	if (iId==0) { 
		fprintf(stdout,"Suma Total de los %ld primeros enteros= %ld\n",ulValorMaximo,ulSumaTotal);
		fprintf(stdout, "Numero Procesos: %d \n" , iNumProcs) ;
		fprintf(stdout, "Tiempo Procesamiento: %f \n\n" , tmpFin-tmpInic);
	}
	MPI_Finalize(); 
	return 0 ;
}
