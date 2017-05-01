#!/usr/bin/env python
import os

from ast_subs import normal_to_packed

family = '4_trunc_V2'

wise_fh = open(os.path.join('../data/', 'WISE_MBA_Pass1_Table_2011.txt'),'r')

wise_objs = {}
header = True
for line in wise_fh:
    if header:
        if  line.lstrip()[0:4] == 'name':
            header = False
        continue
    else:
        chunks = line.strip().split()
        asteroid = chunks[0]
        wise_objs.update({asteroid: line.strip()})

wise_fh.close()
print "Read", len(wise_objs), "WISE objects from file."


        
family_file =  os.path.join('../', 'data', 'family_' + str(family) + '.members')
family_fh = open(family_file, 'r')

family_wise_file =  os.path.join('../', 'data', 'family_' + str(family) + '_WISE.members')
family_wise_fh = open(family_wise_file, 'w')
print >> family_wise_fh, "#ast.name Hmag status    H    G     dia      dia_err    pV     pV_err     eta    eta_err   pIR    pIR_err    w1  w2  w3  w4"

family_asteroids = []
num_matches = 0
for line in family_fh:
    if line.lstrip()[0] == '#' or line.lstrip()[0] == '%':
        continue
    chunks = line.strip().split()
    asteroid = chunks[0].strip()
    H_mag = float(chunks[1])
    status = int(chunks[2])
    unpacked, status = normal_to_packed(asteroid)
    unpacked = unpacked.strip()
    match =  unpacked in wise_objs
    match_string = "No match"
    wise_string = ""
    if match:
        num_matches += 1
        match_string = "Matched "
        wise_string = wise_objs[unpacked][10:]

    print "Checking %9s (%7s) against WISE: %s  (H=%.1f)" % ( asteroid, unpacked, match_string, H_mag)
    print >> family_wise_fh, "%-9s %5.2f  %d    %s" % (asteroid, H_mag, status, wise_string)
    family_asteroids.append(asteroid)
family_fh.close()
family_wise_fh.close()
if num_matches != 0 and len(family_asteroids) != 0:
    print  "%d total matches to the family out of %d members (%.1f%%)" % ( num_matches, len(family_asteroids), (num_matches/float(len(family_asteroids))) * 100.0 )
