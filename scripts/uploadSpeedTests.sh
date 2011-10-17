#!/bin/bash

check_root_f() {
	# need to run tests as root ;-(
	#Make sure only root can run this script
	if [[ $EUID -ne 0 ]]; then
		echo "This script must be run as root"
		exit 1
	fi
}

usage_f() {
	echo "usage:
	-n  <number of iterations> 	# default 1
	-m  <test file size in MB>	# default 1
	-t  <temporary dir>
	-a  <trunk file>
	-s  <server name>
	-l  <login name>
	-p  <login passwd>
	-v  <vebose>

	example: $0 
"
}

# number of iterations
ITERATIONS=1

#file size in MB
FILESIZE=1

TMP_DIR=$PWD
TRUNK_FILE=/tmp/large_file

SERVER_URL=
SERVER_LOGIN=
SERVER_PASSWORD=
VERBOSE=0

SEQUENCE="1 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 10000 20000 40000"

while getopts 'n:m:t:a:s:l:p:v' OPTION
do
	case $OPTION in
		n) ITERATIONS=$OPTARG
			;;
		m) FILESIZE=$OPTARG
			;;		
		t) TMP_DIR=$OPTARG
			;;
		a) TRUNK_FILE=$OPTARG
			;;
		s) SERVER_URL=$OPTARG
			;;
		l) SERVER_LOGIN=$OPTARG
			;;
		p) SERVER_PASSWORD=$OPTARG
			;;
		v) VERBOSE=1
			;;
		?) usage_f >&2
			exit 2
			;;
	esac
done

# check arguments:
if [ ! -f "$TRUNK_FILE" ]; then
	echo "Trunk file not found, creating a new one"
	dd if=/dev/urandom of=$TRUNK_FILE bs=1M count=$FILESIZE > /dev/null 2>&1
else
	echo "Trunk file $TRUNK_FILE found"
	file_size=$(stat -c%s $TRUNK_FILE)
	requested_file_size=$(( 1024 * 1024 * $FILESIZE ))
	if [ $requested_file_size -gt $file_size ]; then
		echo "existing trunk file is not large enough, creating a new one"
		rm -f $TRUNK_FILE
		dd if=/dev/urandom of=$TRUNK_FILE bs=1M count=$FILESIZE > /dev/null 2>&1
	fi
fi

createTestFile() {
	local file_size=$1
	local out_file=$2
	local bs=100000
	local length=$(( $file_size * 1024 * 1024 ))

	( dd bs=1 skip=0 count=0 2> /dev/null
	  dd bs=$bs count=$(($length / $bs)) 2> /dev/null
	  dd bs=$(($length % $bs)) count=1 2> /dev/null
	) < $TRUNK_FILE > $out_file

	# verify file size
	local created_file_size=$(stat -c%s $out_file)
	if [ $created_file_size -ne $length ]; then
		echo "failed to verify test file size: $created_file_size vs $length"
	fi
}


# run webdav tests:
START_TIMER="date +%s%N"
STOP_TIMER="date +%s%N"

for I in $SEQUENCE; do 
	if [ $I -gt $FILESIZE ]; then
		break
	fi

	createTestFile $I ${TMP_DIR}/${I}MB.file
	
	verbose_option=" --silent --show-error -o /dev/null "
	if [ $VERBOSE -eq 1 ]; then
		verbose_option=""
	fi

	start_timer=$($START_TIMER)
	for J in $(seq 1 $ITERATIONS); do
		if [ -z $SERVER_LOGIN ] ; then 
			curl -T ${TMP_DIR}/${I}MB.file ${SERVER_URL}/${I}-${J}MB.file \
				-H Expect: $verbose_option \
				-w "curl report: %{size_upload} %{time_total} %{speed_upload}\n"
		else
			curl -T ${TMP_DIR}/${I}MB.file ${SERVER_URL}/${I}-${J}MB.file \
				-u ${SERVER_LOGIN}:${SERVER_PASSWORD} $verbose_option \
				-w "curl report: %{size_upload} %{time_total} %{speed_upload}\n" 
		fi
	done
	stop_timer=$($STOP_TIMER)

	elapsed_time=$(( $stop_timer - $start_timer ))
	elapsed_time=$(( $elapsed_time / $ITERATIONS ))
        elapsed_time=$(echo $elapsed_time | sed 's/\(.........\)$/\.\1/')

	echo "uploading $I MB elapsed time $elapsed_time (sec)"

	rm ${TMP_DIR}/${I}MB.file
done




