#!/bin/sh
echo "INFO : install-lc3plus.sh"
echo $PWD
LIBFILE=$PWD/libLC3plus.so
HEADERS=$PWD/*.h
mkdir /usr/local/include/LC3plus
cp $LIBFILE /usr/local/lib/
cp $HEADERS /usr/local/include/LC3plus/