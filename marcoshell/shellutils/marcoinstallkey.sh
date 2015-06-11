#!/usr/bin/env bash

function ayuda(){
	echo "Usage: $0 [-h|-n] [-i [identity_file]] [-p port] [[-o <ssh -o options>] ...] [-u user]\n" >&2
	echo "Arguments"
	echo " -h, --help	show this help message and exit"
  	echo " -i [identity_file]   Use only the key(s) contained in identity_file (rather than looking for identities via ssh-add(1) or in the default_ID_file)."
  	echo "                      If the filename does not end in .pub this is added. If the filename is omitted, the default_ID_file is used."
  	echo "                      Note that this can be used to ensure that the keys copied have the comment one prefers and/or extra options applied," 
  	echo "                      by ensuring that the key file has these set as preferred before the copy is attempted."
  	echo " -p [port]"
  	echo " -o [ssh_option]"
  	echo " -n                   dry run"
  	echo " -u                   user"

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

if ! [ -z $AYUDA ];
then
	ayuda
	exit 1
fi

lista=$(marcodiscover  --shell)

for i in $lista; do
	ssh-copy-id $DRY_RUN$FILE$PORT$OPTION$USUARIO$i
done

exit 0
