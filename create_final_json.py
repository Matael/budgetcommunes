#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# create_final_json.py
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


import json
import time
import sys

from glob import glob
from multiprocessing import Queue, Process

OUT_FOLDER = 'final/'

def colorize(dette):
    colors = [
        '#ffffcc',
        '#ffeda0',
        '#fed976',
        '#feb24c',
        '#fd8d3c',
        '#fc4e2a',
        '#e31a1c',
        '#b10026'
    ]

    if dette <= 50:
        return colors[0]
    elif dette > 50 and dette <= 100:
        return colors[1]
    elif dette > 100 and dette <= 250:
        return colors[2]
    elif dette > 250 and dette <= 500:
        return colors[3]
    elif dette > 500 and dette <= 750:
        return colors[4]
    elif dette > 750 and dette <= 1000:
        return colors[5]
    elif dette > 1000 and dette <= 1500:
        return colors[6]
    else:
        return colors[7]

def worker(input):

    for dep in iter(input.get, 'STOP'):

        print('Processing dep. {}'.format(dep))
        # récupération des fichiers de données
        try:
            with open('scripts/{}_data.json'.format(int(dep))) as f:  # use int because of numbering issue
                debts = json.load(f)
                mapper = dict((_,_.replace('OEU','U')) for _ in debts.keys())
                debts = dict((mapper[k],v) for k,v in debts.items())

            with open('shp_extract/pydicts/{}_pydict.json'.format(dep)) as f:
                polys = json.load(f)

        except IOError as e:
            print('Unable to process {} : {}'.format(dep, e))
            continue


        # on crée un objet GeoJSON vide
        geolist = {"type": "FeatureCollection", "features": []}

        for s in debts.keys():
            try :
                new_feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': polys[s][1]
                    },
                    'properties': {
                        '_storage_options': {
                            'color': colorize(debts[s])
                        },
                        'name': polys[s][0],
                        'description': 'Dette de {} €/hab. au 31/12/2012'.format(debts[s]),
                        'dette': debts[s]
                    }
                }

            except KeyError:
                try:
                    key = s.split('-')[0]
                    new_feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Polygon',
                            'coordinates': polys[key][1]
                        },
                        'properties': {
                            '_storage_options': {
                                'color': colorize(debts[s])
                            },
                            'name': polys[key][0],
                            'description': 'Dette de {} €/hab. au 31/12/2012'.format(debts[s]),
                            'dette': debts[s]
                        }
                    }
                except:
                    print(u'Problem with {}'.format(s))

            geolist['features'].append(new_feature)

        print('Saving result to {}{}_final.json'.format(OUT_FOLDER, dep))
        with open('{}{}_final.json'.format(OUT_FOLDER,dep), 'w') as f: f.write(json.dumps(geolist))

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

    # récupération de la liste des départements
    deplist = map(lambda _: _.replace('shp_extract/pydicts/','').split('_')[0], glob('shp_extract/pydicts/*'))
    # chargement des tasks
    for d in deplist:
        input.put(d)

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


if __name__ == '__main__': main()
