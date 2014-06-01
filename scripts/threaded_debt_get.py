#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# threaded_debt_get.py
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

from __future__ import print_function

from bs4 import BeautifulSoup
from requests import get
import re
import time

import json

from multiprocessing import Process, Queue

URLBASE = 'http://alize2.finances.gouv.fr/communes/eneuro/'
PROCESSES = 13

# DEPS = [_ for _ in range(1,96)]
DEPS = [_ for _ in range(31,96)]
for i in [971, 972, 973, 974]: DEPS.append(i)

def worker(input, output):

    for dep,lettre in iter(input.get, 'STOP'):

        soup_depliste = BeautifulSoup(get(URLBASE+'RDep.php?dep={0:03d}&type=BPS&lettre={1}'.format(dep,lettre)).text)
        depliste = {_.text.strip():_.get('href').replace('RComm_gfp', 'tableau') for _ in soup_depliste.findAll('a', {'class' : 'lien'})}

        for ville,url_ville in depliste.items():

            ville = re.sub( r'^([^\(]+)\(([^\)]+)\)', r'\2 \1', ville.encode('utf8').replace('\xc3\x87','C').replace(' ', ''))
            soup_ville = BeautifulSoup(get(URLBASE+url_ville.replace('param=0', 'param=5')).text)
            output.put((
                ville,
                int(soup_ville.find('tr', {'class': 'dette'}).findAll('td',  {'class': 'montantpetitd'})[1].text.replace(' ',''))
            ))


def main():

    input = Queue()
    output = Queue()

    for dep in DEPS:
        print("Now working on dep. {}... ".format(dep), end='')

        # récup des lettres utilisées
        soup_lettres = BeautifulSoup(get(URLBASE+'RDep.php?type=BPS&dep={0:03d}'.format(dep)).text)
        lettres = map(
            lambda _: (dep,_.text),
            soup_lettres.find('tr', {"valign": "baseline"}).findAll('a')
        )
        for l in lettres: input.put(l)

        # start workers
        for i in range(PROCESSES):
            Process(target=worker, args=(input, output)).start()
            input.put('STOP')

        while not input.empty(): time.sleep(5)
        # read the whole queue to a dict and json-store it
        full_list = {}
        while not output.empty():
            res = output.get()
            full_list[res[0]] = res[1]

        print('   DONE. Found {} points.'.format(len(full_list)))
        print('    Now writing results to {}_data.json...'.format(dep), end='')
        try:
            with open("{}_data.json".format(dep),'w') as f:
                f.write(json.dumps(full_list))
            print('   DONE.')
        except IOError as e:
            print('   FAIL : {}'.format(e))


if __name__=='__main__': main()
