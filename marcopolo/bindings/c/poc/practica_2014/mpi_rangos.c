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

#define NUM_MAX	500000000
#define CUANTOS	100

// Lista de valores 
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
/*unsigned int lista[CUANTOS]= {
	1254,12255,1478,5487,50699,80775,12540,25148,96042,54125,
	12,13255,14282,54387,95699,87375,12549,2548,96602,54125};*/
	/*unsigned int lista[CUANTOS]= {
	1254,12255,1478,5487,50699,80775,12540,25148,96042,54125};*/
//ESTRUCTURAS//
typedef struct RETORNO{
	int valor;
	unsigned long long intentos;
	double tiempo;
	}RETORNO;

typedef struct LIMITES{
	int inicio;
	int fin;
	}LIMITES;

//PROTOTIPOS//
void tipoLimite(LIMITES *datos,MPI_Datatype *tipoMPI);
void tipoRetorno(RETORNO *datos,MPI_Datatype *tipoMPI);
void busca_numero(unsigned int numero, unsigned long long * intentos, double * tpo);
double mygettime(void);

///////////////////////////////////////////////////////////////////
/*
	FUNCION MAIN
*/
///////////////////////////////////////////////////////////////////
int main(int argc,char** argv) {
	//DECLARACION DE VARIABLES//
	double	fTpo,fTpoInicial=0.0, fTpoFinal,fTpoAcumulado=0.0,fTpoMax=0.0;
	unsigned long long  ullIntentosAcumulados=0,ulIntentos,ullIntentosMax=0;
	int i,numprocs,id,numerocalc,reparto,resto;
	MPI_Status status;
	MPI_Datatype MPI_LIM,MPI_RET;
	LIMITES recibida;
	RETORNO ret;

	/////////////////////////////////////////////////////////
	//COMIENZO DE MPI                                      //
	/////////////////////////////////////////////////////////
	MPI_Init(&argc,&argv);
	MPI_Comm_size(MPI_COMM_WORLD,&numprocs);
	MPI_Comm_rank(MPI_COMM_WORLD,&id);
	
	tipoLimite(&recibida,&MPI_LIM);
	tipoRetorno(&ret,&MPI_RET);

	if(id==0){//Prceso E/S
		printf("RAND_MAX: %d\n",RAND_MAX);
		printf("NUM_MAX:  %d\n",NUM_MAX);
		printf("UINT_MAX: %u\n",UINT_MAX);
		printf("Semilla:  %d\n",1);
	}else{
		srand(1);
	}


	fTpoInicial=MPI_Wtime();

	//Repartimos los números entre los procesos
	if(id==0){ //Proceso E/S
		numerocalc=numprocs-1;
		//Hay más procesos que números
		if(numerocalc>=CUANTOS){
			for(i=0;i<numerocalc;i++){
				if(i>=CUANTOS) recibida.inicio=recibida.fin=-1;
				else{
					recibida.inicio=i;
					recibida.fin=i;
				}
				MPI_Send(&recibida,1,MPI_LIM,i+1,10,MPI_COMM_WORLD);
			}
		//Hay más números que procesos
		}else{
			reparto=CUANTOS/numerocalc;
			resto=CUANTOS%numerocalc;
			recibida.inicio=recibida.fin=0;
			
			for(i=0;i<numerocalc;i++){
				recibida.fin=reparto+recibida.inicio-1;
				if(resto>0){ //El reparto no es exacto
					recibida.fin++;
					resto--;
				}
				
				MPI_Send(&recibida,1,MPI_LIM,i+1,10,MPI_COMM_WORLD);
				recibida.inicio=recibida.fin+1;
			}
		}
		//Esperamos a que nos lleguen todos los números
		for(i=0;i<CUANTOS;i++){
			MPI_Recv(&ret,1,MPI_RET,MPI_ANY_SOURCE,MPI_ANY_TAG,MPI_COMM_WORLD,&status);
			printf("%d) Numero: %u, Intentos: %llu, Tiempo: %f\n",i,ret.valor,ret.intentos,ret.tiempo);
			fTpoAcumulado+=ret.tiempo;
			ullIntentosAcumulados+=ret.intentos;

			if(ret.tiempo>fTpoMax)
				fTpoMax=ret.tiempo;
			if(ret.intentos>ullIntentosMax)
				ullIntentosMax=ret.intentos;
		}
		fTpoFinal=MPI_Wtime();
		//Se han calculado todos los números
		fprintf(stdout,"Intentos Acumulados: %llu \n",ullIntentosAcumulados);
		fprintf(stdout,"Tiempo Acumulado:    %f   \n",fTpoAcumulado);
		fprintf(stdout,"Tiempo Total:        %f   \n",fTpoFinal-fTpoInicial);
		fprintf(stdout,"Max Intentos:        %llu \n",ullIntentosMax);
		fprintf(stdout,"Max Tiempo:          %f   \n\n",fTpoMax);
		
		MPI_Finalize();

	}else{ //Procesos calculadores
		MPI_Recv(&recibida,1,MPI_LIM,0,10,MPI_COMM_WORLD,&status);
		
		if (recibida.inicio!=-1){
			for(i=recibida.inicio;i<=recibida.fin;i++){
				busca_numero(lista[i],&ulIntentos,&fTpo);
				ret.valor=lista[i];
				ret.intentos=ulIntentos;
				ret.tiempo=fTpo;
				MPI_Send(&ret,1,MPI_RET,0,20,MPI_COMM_WORLD);
			}
			
		}
		MPI_Finalize();
	}
	/////////////////////////////////////////////////////////
	return 0;
}

///////////////////////////////////////////////////////////////////
/*
	FUNCION TIPOLIMITE
*/
///////////////////////////////////////////////////////////////////
void tipoLimite(LIMITES *datos,MPI_Datatype *tipoMPI){
	MPI_Datatype tipos[2];
	int longitudes[2];
	MPI_Aint direcciones[3];
	MPI_Aint desplazamiento[2];
	int i;

	MPI_Address(datos,&direcciones[0]);
	MPI_Address(&(datos->inicio),&direcciones[1]);
	MPI_Address(&(datos->fin),&direcciones[2]);

	for(i=0;i<2;i++){
		tipos[i]=MPI_INT;
		longitudes[i]=1;
		desplazamiento[i]=direcciones[i+1]-direcciones[0];
	}

	MPI_Type_struct(2,longitudes,desplazamiento,tipos,tipoMPI);
	MPI_Type_commit(tipoMPI);
}
///////////////////////////////////////////////////////////////////
/*
	FUNCION TIPORETORNO
*/
///////////////////////////////////////////////////////////////////
void tipoRetorno(RETORNO *datos,MPI_Datatype *tipoMPI){
	MPI_Datatype tipos[3];
	int longitudes[3];
	MPI_Aint direcciones[4];
	MPI_Aint desplazamiento[3];
	int i;

	tipos[0]=MPI_INT;
	tipos[1]=MPI_UNSIGNED_LONG_LONG;
	tipos[2]=MPI_DOUBLE;

	MPI_Address(datos,&direcciones[0]);
	MPI_Address(&(datos->valor),&direcciones[1]);
	MPI_Address(&(datos->intentos),&direcciones[2]);
	MPI_Address(&(datos->tiempo),&direcciones[3]);

	for(i=0;i<3;i++){
		longitudes[i]=1;
		desplazamiento[i]=direcciones[i+1]-direcciones[0];
	}

	MPI_Type_struct(3,longitudes,desplazamiento,tipos,tipoMPI);
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

		//printf("%llu\n",*intentos);
	} while (!bSalir);		

	t2=mygettime();
	*tpo=t2-t1;
}
