#!/bin/zsh
#
# shp_dl.sh
#
# Copyright © 2014 Mathieu Gaborit (matael) <mathieu@matael.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

