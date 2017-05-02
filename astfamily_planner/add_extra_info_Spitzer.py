#!/usr/bin/env python
import os

from ast_subs import normal_to_packed
from source_subs import read_mpcorb_file, split_trilling_targets


astorb_file = os.path.join(os.getenv('HOME'),'Asteroids','Astrometrica','Tutorials','MPCOrb.dat')
lines1,lines2,lines3 = read_mpcorb_file(astorb_file)
astorb_lines = lines1+lines2+lines3

input_file =  os.path.join('../', 'data', 'Trilling_2017_Spitzer')
output_file =  os.path.join('../', 'data', 'Trilling_2017_Spitzer_extrainfo.csv')

#input_file =  os.path.join('../', 'data', 'Trilling_2017_Spitzer_test')
#output_file =  os.path.join('../', 'data', 'Trilling_2017_Spitzer__test_extrainfo.csv')

input_fh = open(input_file, 'r')
output_fh = open(output_file, 'w')

print >> output_fh, "#Ast,Name,MPC,1st,Nobs,HMag,G"
for line in input_fh:
    # Skip header line
    if line.lstrip()[0] == '#' or line.lstrip()[0] == '%':
        continue
    number, desig = split_trilling_targets(line)
#    print "number=%s, desig=%s" % (number,desig)
    if number != '':
        number_or_desig = number
    else:
        number_or_desig = desig
    try:
#        print number_or_desig
        packed_number_or_desig, status = normal_to_packed(number_or_desig)
    except ValueError:
        print "Problem with number= %s, desig= %s\nline= %s" % (number, desig, line)
        continue
    elements = [x for x in astorb_lines if (x[0:7].strip() == packed_number_or_desig.strip() or number_or_desig in x[166:194].strip())]
    H = '     '
    G = '   '
    if len(elements) > 0:
        H = elements[0][8:13]
        G = elements[0][15:19]
    else:
        print "No match for", number_or_desig, packed_number_or_desig
    new_line = "NEA ,%11s,%8s,  0,%s,%s" % (number_or_desig, packed_number_or_desig, H, G)
    print >> output_fh, new_line 
input_fh.close()
output_fh.close()
