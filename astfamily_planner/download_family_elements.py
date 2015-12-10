#!/usr/bin/env python
import json
import os
from datetime import datetime

from source_subs import update_MPC_orbit, split_asteroid

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat(sep=' ')
        return serial
    raise TypeError ("Type not serializable")

def write_bodies_to_element_file(data_path, family, bodies):
    '''Writes a list of dictionaries of asteroid name + elements out in JSON
    format. The file is written to <data_path>/family_<family>.elements
    and the number of bodies written is returned.'''

    num_written = None
    if len(bodies) > 0:
        family_elements =  os.path.join(data_path, 'family_' + str(family) + '.elements')
        with open(family_elements, 'w') as f:
            json.dump(bodies, f,default=json_serial,indent=2)
        num_written = len(bodies)

    return num_written

family = '4_trunc'
data_path =  os.path.join('../', 'data')
family_file =  os.path.join(data_path, 'family_' + str(family) + '.members')
family_fh = open(family_file, 'r')

bodies = []
for line in family_fh:
    if line.lstrip()[0] == '%' or line.lstrip()[0] == "#" :
        print "Skipped header"
        continue
    chunks = line.strip().split()
    # Check if of the form '2014PD25'
    asteroid = split_asteroid(chunks[0])
    print "Downloading elements for", asteroid
    elements = update_MPC_orbit(asteroid)
    bodies.append( { asteroid : elements } )

family_fh.close()
print "Wrote", write_bodies_to_element_file(data_path, family, bodies), "elements out"
