#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# threaded_debt_get.py
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
