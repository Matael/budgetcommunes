#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# convert.py
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


import shapefile as sf
import unicodedata
import string
import json
import time
import sys

from glob import glob
from multiprocessing import Queue, Process

def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data.decode('utf8')) if x in string.ascii_letters+"- '").upper()


def worker(input):

    for file in iter(input.get, 'STOP'):

        # extraire le numéro de département
        depnum = file.split('-')[0]

        print('Processing : {}'.format(file))

        # ouvrir le shp
        sarthe_shp = sf.Reader(file)

        # création de la liste du json final et du dict
        shapes = sarthe_shp.iterShapes()
        records = sarthe_shp.iterRecords()

        outjson = []
        python_dict = {}
        for r in records:
            s = shapes.next()

            name = remove_accents(r[0])
            coords = [map(lambda point: map(lambda _: str(_), point), s.points)]

            outjson.append({
                'type':"Feature",
                'geometry':{
                    'type':"Polygon",
                    'coordinates': coords
                },
                'properties':{
                    'name': name
                }
            })
            python_dict[name] =  (r[0], coords)

        print('Writing GeoJSON to {}_polygons.geojson'.format(depnum))
        with open('{}_polygons.geojson'.format(depnum), 'w') as f: f.write(json.dumps(outjson))
        print('Writing Python Dict to {}_pydict.json'.format(depnum))
        with open('{}_pydict.json'.format(depnum), 'w') as f: f.write(json.dumps(python_dict))


def main():

    # le nombre de workers à utiliser est passé en argument
    # si rien n'est donné, on utilise une valeur par défaut de 3
    if len(sys.argv) > 1:
        num_workers = int(sys.argv[1])
    else:
        num_workers = 3

    print('Run using {} workers'.format(num_workers))

    # création de la task list
    input = Queue()

    # chargement des tasks
    for f in glob("*.shp"):
        input.put(f)

    workers_list = []
    for i in range(num_workers):
        workers_list.append(
            Process(target=worker,
                   args=(input,)
            )
        )
        workers_list[-1].start()
        input.put('STOP')

    time.sleep(2)
    for i in workers_list: i.join()


if __name__=='__main__': main()
