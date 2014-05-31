#!/bin/zsh

urlbase='http://export.openstreetmap.fr/contours-administratifs/communes/'

worker() {
	while (true) {

		read -u 0
		shp=$REPLY

		print "$1: Downloading $shp"
		wget -q $urlbase$shp -O $shp;
		echo "$1: Unpacking $shp"
		tar xzvf $shp
		rm $shp
		echo "$1: DONE $shp"
	}
}

mkfifo pipe
worker "W0" < pipe & workers+=($!)
worker "W1" < pipe & workers+=($!)
worker "W2" < pipe & workers+=($!)
worker "W3" < pipe & workers+=($!)

for shp in $(cat shp_liste.txt); do
	print $shp >> pipe
done;

wait ${worker[*]}
rm pipe
exit 0

