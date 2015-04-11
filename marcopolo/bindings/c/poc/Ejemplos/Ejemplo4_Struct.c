# include "mpi.h"
# include <stdio.h>


typedef struct {
	int iA;
	int iB;
	int iC;
} Tipo_Datos_Entrada;

double Opera(Tipo_Datos_Entrada datos, int iID)
{
	return datos.iA*iID*iID+datos.iB*iID+datos.iC;
}


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


void Crea_Tipo_Derivado_Salida(Tipo_Datos_Entrada * pDatos, MPI_Datatype * pMPI_Tipo_Datos)
{
	MPI_Datatype tipos[3];
	int longitudes[3];
	MPI_Aint direcc[4];
	MPI_Aint desplaz[3];
	
	tipos[0]=MPI_INT;
	tipos[1]=MPI_INT;
	tipos[2]=MPI_INT;
	
	longitudes[0]=1;
	longitudes[1]=1;
	longitudes[2]=1;
	
	MPI_Address(pDatos, &direcc[0]);
	MPI_Address(&(pDatos->iA), &direcc[1]);
	MPI_Address(&(pDatos->iB), &direcc[2]);
	MPI_Address(&(pDatos->iC), &direcc[3]);
	
	desplaz[0]=direcc[1]-direcc[0];
	desplaz[1]=direcc[2]-direcc[0];
	desplaz[2]=direcc[3]-direcc[0];
	
	MPI_Type_struct(3, longitudes, desplaz, tipos, pMPI_Tipo_Datos);
	
	MPI_Type_commit(pMPI_Tipo_Datos);
}

#define MSG_RESULTADO 50
#define MSG_DATOS_ENTRADA 55


int main (int argc , char **argv) {
	int i;
	int iId ; 
	int iNumProcs; 
	double tmpInic = 0.0; 
	double tmpFin; 
	double fSuma=0.0;
	double fRecv=0.0;
	int etiqueta;
	MPI_Status status;	
	MPI_Datatype MPI_Tipo_Datos_Entrada;
	Tipo_Datos_Entrada datos_entrada;


	MPI_Init (&argc ,&argv); 						
	MPI_Comm_rank(MPI_COMM_WORLD,&iId ); 			
	MPI_Comm_size(MPI_COMM_WORLD, & iNumProcs ); 	
	
	// Para saber donde se ejecuta cada cosa
	Obten_Nombre_Procesos(iId, iNumProcs);
	
	tmpInic=MPI_Wtime(); 
	
	// El id=0 espera los resultados
	if (iId==0)
	{
		etiqueta=MSG_RESULTADO;
		for (i=2;i<iNumProcs;i=i+2)
		{
			MPI_Recv(&fRecv,1, MPI_DOUBLE, i, etiqueta, MPI_COMM_WORLD, &status);
			fSuma+=fRecv;
		}
	}	
	// Proceso impar
	else 
	{
		Crea_Tipo_Derivado_Salida(&datos_entrada,&MPI_Tipo_Datos_Entrada);
		
		if (iId%2==1)
		{
			etiqueta=MSG_DATOS_ENTRADA;
			datos_entrada.iA=iId;
			datos_entrada.iB=iId+1;
			datos_entrada.iC=iId+2;
			MPI_Send(&datos_entrada,1,MPI_Tipo_Datos_Entrada,iId+1,etiqueta,MPI_COMM_WORLD);
		}
		// Proceso par
		else
		{
			etiqueta=MSG_DATOS_ENTRADA;
			MPI_Recv(&datos_entrada,1,MPI_Tipo_Datos_Entrada,iId-1,etiqueta,MPI_COMM_WORLD,&status);
			fRecv=Opera(datos_entrada,iId);
			etiqueta=MSG_RESULTADO;
			MPI_Send(&fRecv,1,MPI_DOUBLE,0,etiqueta,MPI_COMM_WORLD);
		}
	}
	tmpFin =MPI_Wtime(); 	
	
	if (iId==0) { 
		fprintf(stdout,"Suma Total = %f\n",fSuma);
		fprintf(stdout, "Numero Procesos: %d \n" , iNumProcs) ;
		fprintf(stdout, "Tiempo Procesamiento: %f \n\n" , tmpFin-tmpInic);
	}
	MPI_Finalize(); 
	return 0;
}


