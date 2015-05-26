#!/usr/bin/env bash

function ayuda(){
	printf 'Usage: %s [-h|-n] [-i [identity_file]] [-p port] [[-o <ssh -o options>] ...] [-u user]\n' "$0" >&2
}

while [[ $# -ge 1 ]]
do

key="$1"

case $key in
	
	-h)
	AYUDA=YES
	shift
	;;
	-i)
	FILE="-i $2 "
	shift
	;;
	-p)
	PORT="-p $2 "
	shift
	;;
	-o)
	OPTION="-o $2 "
	shift
	;;
	-n)
	DRY_RUN="-n "
	shift
	;;
	-u)
	USUARIO="$2@"
	shift
	;;
    *)
    ayuda      # opción desconocida
    exit 1
    ;;
esac
shift
done

if ! [ -z $AYUDA ] 
then
	ayuda
	exit 1
fi

lista=$(marcodiscover.py  --shell)

for i in $lista; do
	ssh-copy-id $DRY_RUN$FILE$PORT$OPTION$USUARIO$i
done

exit 0
