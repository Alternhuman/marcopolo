#!/usr/bin/env bash

function ayuda(){
	printf 'Usage: %s [-h|-?|-n] [-i [identity_file]] [-p port] [[-o <ssh -o options>] ...] [user]\n' "$0" >&2
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
        -l)
        USER="-l $2"
        shift
        ;;
        -p)
        PORT="-p $2"
        shift
        ;;
        *)
        COMMAND="$1"      # opción desconocida
        shift
	;;
esac

done

lista=$(marcodiscover.py  --shell)

for i in $lista; do
	ssh $USER $PORT $i $COMMAND
done

exit 0
