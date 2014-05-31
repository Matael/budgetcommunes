#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# convert.py
#
# Copyright © 2014 Mathieu Gaborit (matael) <mathieu@matael.org>
#
#
# Distributed under WTFPL terms
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.
#

"""

"""


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
