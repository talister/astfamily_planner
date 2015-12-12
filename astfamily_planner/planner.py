#!/usr/bin/env python
import os
import json
from datetime import datetime, timedelta

import logging

from ephem_subs import call_compute_ephem, compute_ephem, determine_darkness_times

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
mag_limit = 21.5

bodies = read_elements_list(data_path, family)
print "Read in ", len(bodies), "asteroids and elements."

logging.basicConfig(filename='planner.log', level=logging.INFO)

line_fmt = "%s    %s %s    %s    %s   %3s   %3s  %4s %s"
for asteroid in bodies[-2:-1]:
    ast_name = str(asteroid.keys()[0])
    ast_fh = open(os.path.join(data_path, ast_name.replace(' ', '') + '_output'), 'w')
    for site in sites[1:2]:
        ast_elems = asteroid.values()[0]
        print "Working on", ast_name, "at", site
        print >> ast_fh, "# %s  (H=%2.1f) at %s" % ( ast_name, ast_elems['abs_mag'], site )
        print >> ast_fh, "#UTC date/time          RA (J2000.0) Dec     PhaseA    Vmag   Alt MoonD Score  H.A."
        
        d = obs_start
        while d <= obs_end:
            dark_start, dark_end = determine_darkness_times(site, d)
            emp = call_compute_ephem(ast_elems, dark_start, dark_end, site, obs_step, alt_limit, mag_limit)
            for line in emp:
# 0         1  2   3          4    5    6   7           8        9      10   11
# datetime RA Dec PhaseAngle Mag Speed  Alt MoonPhase MoonDist MoonAlt Score HA
                print >> ast_fh, line_fmt % (line[0], line[1], line[2], line[3], line[4], line[6], line[8], line[10], line[11])
            d = d + timedelta(days=1)

    ast_fh.close()
