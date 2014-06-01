Budget Communes
===============

Il s'agit de récupérer les endettements par habitant au 31/12/2012.

Récupération des données d'endettement
--------------------------------------


    $ cd scripts
    $ python threaded_debt_get.py


Récupération des shp
--------------------

    $ cd shp_extract
    $ ./shp_dl.sh

Attention, il y a environ 300MB.

Conversion shp->{geojson,pydict.json}
-------------------------------------

    $ cd shp_extract
    $ python convert N

Avec `N` le nombre de threads

Attention, génère beaucoup de données.

Génération des json finaux
--------------------------

    $ python create_final_json.py N

Avec `N` le nombre de threads
