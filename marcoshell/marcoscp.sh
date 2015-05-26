#!/usr/bin/env bash

function ayuda(){
	printf 'Usage: %s [-h] [-r] <file> <user>\n' "$0" >&2
}

while [[ $# -ge 1 ]]
do

    key="$1"

    case $key in
	
        -h)
        ayuda
        exit 0
        shift
        ;;
        -d)
        DIRECTORY="$2"
        shift
        ;;
	-l)
	USUARIO="$2@"
	shift
	shift
	;;
	-r)
	RECURSIVE="-r "
	;;
        *)
        DIRECTORIES="$DIRECTORIES $1"      # opción desconocida
        shift
	;;
esac

done

lista=$(marcodiscover.py  --shell)

for i in $lista; do
	scp $RECURSIVE $DIRECTORIES $USUARIO$i:$DIRECTORY
done

exit 0
