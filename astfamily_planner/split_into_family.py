#!/usr/bin/env python
import os

family = 4 
data_file = os.path.join('../', 'data','all.members')

try:
    data_fh = open(data_file, 'r')
except:
    print "Could not open", data_file, ". Exiting."
    os.sys.exit(-1)

print "Reading", data_file,", looking for family #", family
family_file =  os.path.join('../', 'data', 'family_' + str(family) + '.members')
family_fh = open(family_file, 'w')
print >> family_fh, "#ast.name  Hmag   status"

num_family = 0

for line in data_fh.readlines():
    if line.lstrip()[0] == '%' or line.lstrip()[0] == "#" :
        print "Skipped header"
        continue
    chunks = line.strip().split()
    family1 = int(chunks[3])
    if family1 == family:
        asteroid = chunks[0]
        H_mag = float(chunks[1])
        status = int(chunks[2])
        print "Found match for %9s with H=%.2f and status=%d" % (asteroid, H_mag, status)
        print >> family_fh, "%-9s %.2f %d" % (asteroid, H_mag, status)
        num_family += 1
print "Wrote %d family members to %s" % ( num_family, family_file )

data_fh.close()
family_fh.close()
