#!/usr/bin/env python
import os
import numpy as np

family = 4
H_min = 9.0
H_max = 18.0
nbins = int((max(H_max, H_min) - min(H_max, H_min)) / 0.5) + 0
print "Number of bins = %d between H= %.1f-%.1f" % ( nbins, H_min, H_max)
family_file =  os.path.join('../', 'data', 'family_' + str(family) + '.members')
family_fh = open(family_file, 'r')

H_mags = []
for line in family_fh:
    if line.lstrip()[0] == '#' or line.lstrip()[0] == '%':
        continue
    chunks = line.strip().split()
    H_mag = float(chunks[1])
    H_mags.append(H_mag)
family_fh.close()

hist, bin_edges = np.histogram(H_mags, nbins, (H_min, H_max))
print
i=0
while i<len(hist):
    print "%-4.1f-%-4.1f: %4d" % (bin_edges[i], bin_edges[i+1], hist[i])
    i += 1
