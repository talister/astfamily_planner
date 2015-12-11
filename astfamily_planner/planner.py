#!/usr/bin/env python
import os
import json
from datetime import datetime, timedelta

import logging

from ephem_subs import call_compute_ephem, compute_ephem

def read_elements_list(data_path, family):
    
    family_elements =  os.path.join(data_path, 'family_' + str(family) + '.elements')
    with open(family_elements, 'r') as f:
        bodies = json.load(f)

    return bodies

family = '4_trunc'
data_path =  os.path.join('../', 'data')
sites = ['W85', 'K92', 'Q63']
obs_start = datetime(2015, 12, 10, 18, 0, 0)
obs_end = datetime(2016, 4, 1, 0, 0, 0)
obs_step = '60m'
alt_limit = 30.0 

bodies = read_elements_list(data_path, family)
print "Read in ", len(bodies), "asteroids and elements."

logging.basicConfig(filename='planner.log', level=logging.DEBUG)

for asteroid in bodies[0:1]:
    for site in sites[1:2]:
        print "Working on", str(asteroid.keys()[0]),"at", site
        d = obs_start
        emp = call_compute_ephem(asteroid.values()[0], obs_start, obs_end, site,obs_step, alt_limit)
        for line in emp:
            print line[0], "  ", line[1], line[2], "  ",line[3],"  ", line[4], " ", line[6]
