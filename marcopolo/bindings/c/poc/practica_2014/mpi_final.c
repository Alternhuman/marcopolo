///////////////////////////////////////////////////////////////////
/*
	MPI
	Diego Martin Arroyo: 70825993T
	Antonio Javier Moreno Hernandez: 7109304V
	Sergio Sanchez Gonzalez: 70900759Q
	Alexandra Vicente Sanchez:  70918191Z
*/
///////////////////////////////////////////////////////////////////
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <mpi.h>
#include <sys/time.h>
#include <time.h>
#include <float.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#define NUM_MAX	500000000
#define CUANTOS	100

////////////////////
//LISTA DE VALORES//
////////////////////
unsigned int lista[CUANTOS]= {
	1254,12255,1478,5487,50699,80775,12540,25148,96042,54125,
	12,13255,14282,54387,95699,87375,12549,2548,96602,54125,
	124,12455,24782,52487,85699,87475,12548,21548,96942,52125,
	154,12555,14278,54817,75699,87675,12547,12548,96842,54425,
	254,12565,14728,54287,65699,87785,12546,25418,96642,54155,
	2254,12755,14782,54487,55699,87775,12351,25148,95642,54525,
	3254,12855,42728,54867,45699,87975,12531,12548,94642,54425,
	4254,19255,24278,58487,35699,80775,12521,22548,93642,54325,
	5254,10255,22478,54897,25699,8775,22541,32548,91642,54145,
	6254,12055,21478,54807,15699,8775,12541,42548,92642,54135};
	
///////////////
//ESTRUCTURAS//
///////////////
typedef struct RETORNO{
	int valor;
	unsigned long long intentos;
	double tiempo;
	int id;
	}RETORNO;

typedef struct LIMITE{
	int indice;
	}LIMITE;

//////////////
//PROTOTIPOS//
//////////////
void tipoLimite(LIMITE *datos,MPI_Datatype *tipoMPI);
void tipoRetorno(RETORNO *datos,MPI_Datatype *tipoMPI);
void busca_numero(unsigned int numero, unsigned long long * intentos, double * tpo);
double mygettime(void);

///////////////////////////////////////////////////////////////////
/*
	FUNCION MAIN
*/
///////////////////////////////////////////////////////////////////
int main(int argc,char** argv) 
{
	//DECLARACION DE VARIABLES//
	double	fTpo,fTpoInicial=0.0, fTpoFinal,fTpoAcumulado=0.0,fTpoMax=0.0;
	unsigned long long  ullIntentosAcumulados=0,ulIntentos,ullIntentosMax=0;
	int i,numprocs,id,numerocalc;
	MPI_Status status;
	MPI_Datatype MPI_LIM,MPI_RET;
	LIMITE recibida;
	RETORNO ret;
	int aux=1, id_ret, pendientes, calc_activas=0, num_rest=0;
	int out, save_out;
	char filename[30];
	
	/////////////////////////////////////////////////////////
	//COMIENZO DE MPI                                      //
	/////////////////////////////////////////////////////////
	MPI_Init(&argc,&argv);
	MPI_Comm_size(MPI_COMM_WORLD,&numprocs);
	MPI_Comm_rank(MPI_COMM_WORLD,&id);
	
	tipoLimite(&recibida,&MPI_LIM);
	tipoRetorno(&ret,&MPI_RET);

	if(numprocs < 2){
		if(id == 0){
			fprintf(stdout, "El número de procesos indicado no es suficiente. Terminando\n");
		}
		MPI_Finalize();
		return 1;
	}
	if(id==0)
	{
		//Prceso E/S//
		if(argc == 2)
		{
			sprintf(filename, "cout_%d.csv", numprocs);
			out = open(filename, O_RDWR|O_CREAT|O_APPEND, 0600);
			save_out = dup(fileno(stdout));
			if (-1 == dup2(out, fileno(stdout))) { perror("cannot redirect stdout"); return 255; }
		}
		else		
		{
			fprintf(stdout, "RAND_MAX: %d\n",RAND_MAX);
			fprintf(stdout, "NUM_MAX:  %d\n",NUM_MAX);
			fprintf(stdout, "UINT_MAX: %u\n",UINT_MAX);
			fprintf(stdout, "Semilla:  %d\n",1);
		}

		//Repartimos los números entre los procesos
		fTpoInicial=MPI_Wtime();
		numerocalc=numprocs-1;
		for(i=0;i<numerocalc;i++)
		{
			if(i>=CUANTOS)
			{
				//El indice -1 indica que el proceso no es necesario, y en cuando recibe la estructura muere
				recibida.indice=-1;
			}
			else
			{
				recibida.indice=i;
				calc_activas++;
				num_rest++;
			}
			MPI_Send(&recibida,1,MPI_LIM,i+1,10,MPI_COMM_WORLD);
		}

		while(calc_activas!=0)
		{
			MPI_Recv(&ret,1,MPI_RET,MPI_ANY_SOURCE,MPI_ANY_TAG,MPI_COMM_WORLD,&status);
			//Hemos recibido un mensaje
			if(argc != 2)
			{
				fprintf(stdout, "\n%d) Numero: %u, Intentos: %llu, Tiempo: %f, Proceso: %d",aux,ret.valor,ret.intentos,ret.tiempo,ret.id);
			}
			else
			{
				fprintf(stdout, "%u,%llu,%f,%d\n",ret.valor,ret.intentos,ret.tiempo,ret.id);
			}
		
			fTpoAcumulado+=ret.tiempo;
			ullIntentosAcumulados+=ret.intentos;
			id_ret=ret.id;
			aux++;
			if(ret.tiempo>fTpoMax)
				fTpoMax=ret.tiempo;
			if(ret.intentos>ullIntentosMax)
				ullIntentosMax=ret.intentos;

			if(num_rest<CUANTOS)
			{
				recibida.indice=num_rest;
				num_rest++;
			}
			else
			{
				recibida.indice=-1;
				calc_activas--;
			}
			MPI_Send(&recibida,1,MPI_LIM,id_ret,10,MPI_COMM_WORLD);
		}


		fTpoFinal=MPI_Wtime();
		//Se han calculado todos los números
		if(argc != 2)
		{
			fprintf(stdout,"\nIntentos Acumulados: %llu \n",ullIntentosAcumulados);
			fprintf(stdout,"Tiempo Acumulado:    %f   \n",fTpoAcumulado);
			fprintf(stdout,"Tiempo Total:        %f   \n",fTpoFinal-fTpoInicial);
			fprintf(stdout,"Max Intentos:        %llu \n",ullIntentosMax);
			fprintf(stdout,"Max Tiempo:          %f   \n\n",fTpoMax);
		}
		else
		{
			fprintf(stdout, ",,,,\n");
			fprintf(stdout, "Intentos acumulados, Tiempo acumulado, Tiempo total, Max intentos, Max tiempo\n");
			fprintf(stdout,"%llu,%f,%f,%llu,%f\n",ullIntentosAcumulados, fTpoAcumulado,fTpoFinal-fTpoInicial,ullIntentosMax,fTpoMax);

			fflush(stdout); close(out);

    		dup2(save_out, fileno(stdout));

    		close(save_out);
		}
		MPI_Finalize();
		return 0;
	}
	else
	{ 
		//Procesos calculadores
		srand(1);
		do{
			MPI_Recv(&recibida,1,MPI_LIM,0,10,MPI_COMM_WORLD,&status);
			if(recibida.indice!=-1)
			{
				busca_numero(lista[recibida.indice],&ulIntentos,&fTpo);
				ret.valor=lista[recibida.indice];
				ret.intentos=ulIntentos;
				ret.tiempo=fTpo;
				ret.id=id;
				MPI_Send(&ret,1,MPI_RET,0,20,MPI_COMM_WORLD);
			}
			else
			{
				MPI_Finalize();
				return 0;
			}
		}while(recibida.indice!=-1);	
	}
	/////////////////////////////////////////////////////////
}

///////////////////////////////////////////////////////////////////
/*
	FUNCION TIPOLIMITE
*/
///////////////////////////////////////////////////////////////////
void tipoLimite(LIMITE *datos,MPI_Datatype *tipoMPI){
	MPI_Datatype tipos[1];
	int longitudes[1];
	MPI_Aint direcciones[2];
	MPI_Aint desplazamiento[1];

	tipos[0]=MPI_INT;

	longitudes[0]=1;

	MPI_Address(datos,&direcciones[0]);
	MPI_Address(&(datos->indice),&direcciones[1]);

	desplazamiento[0]=direcciones[1]-direcciones[0];

	MPI_Type_struct(1,longitudes,desplazamiento,tipos,tipoMPI);
	MPI_Type_commit(tipoMPI);
}
///////////////////////////////////////////////////////////////////
/*
	FUNCION TIPORETORNO
*/
///////////////////////////////////////////////////////////////////
void tipoRetorno(RETORNO *datos,MPI_Datatype *tipoMPI){
	MPI_Datatype tipos[4];
	int longitudes[4];
	MPI_Aint direcciones[5];
	MPI_Aint desplazamiento[4];
	int i;

	tipos[0]=MPI_INT;
	tipos[1]=MPI_UNSIGNED_LONG_LONG;
	tipos[2]=MPI_DOUBLE;
	tipos[3]=MPI_INT;

	MPI_Address(datos,&direcciones[0]);
	MPI_Address(&(datos->valor),&direcciones[1]);
	MPI_Address(&(datos->intentos),&direcciones[2]);
	MPI_Address(&(datos->tiempo),&direcciones[3]);
	MPI_Address(&(datos->id),&direcciones[4]);

	for(i=0;i<4;i++){
		longitudes[i]=1;
		desplazamiento[i]=direcciones[i+1]-direcciones[0];
	}

	MPI_Type_struct(4,longitudes,desplazamiento,tipos,tipoMPI);
	MPI_Type_commit(tipoMPI);
}
///////////////////////////////////////////////////////////////////
/*
	FUNCION MYGETTIME
*/
///////////////////////////////////////////////////////////////////
double mygettime(void) {
	struct timeval tv;
	if(gettimeofday(&tv, 0) < 0) perror("oops");

	return (double)tv.tv_sec + (0.000001 * (double)tv.tv_usec);
}
///////////////////////////////////////////////////////////////////
/*
	FUNCION BUSCA_NUMERO
*/
///////////////////////////////////////////////////////////////////
void busca_numero(unsigned int numero, unsigned long long * intentos, double * tpo)
{
	short bSalir=0;
	double t1,t2;

	*intentos=0;
	t1=mygettime();
	srand(1);

	do{
		(*intentos)++;
		if ((rand()%NUM_MAX+1)==numero) bSalir=1;
	} while (!bSalir);		

	t2=mygettime();
	*tpo=t2-t1;
}
