#!/usr/bin/env python
import os

family = '4'
family_file =  os.path.join('../', 'data', 'family_' + str(family) + '_WISE.members')
family_fh = open(family_file, 'r')

num_req = 100
num_skip = 2
horizon = 5

lines_read = 0
asteroids = []
for line in family_fh:
    # Skip header line
    if line.lstrip()[0] == '#' or line.lstrip()[0] == '%':
        header = line
        continue
    # Skip <num_skip> objects at the top (usually because they are too bright)
    lines_read += 1
    if lines_read <= num_skip:
        continue
    asteroids.append(line.strip())

family_fh.close()
num_asteroids = len(asteroids)
print "Read %d asteroids" % num_asteroids

trunc_family_file =  os.path.join('../', 'data', 'family_' + str(family) + '_trunc_V2.members')
if os.path.exists(trunc_family_file):
    print "File", trunc_family_file, "already exists, not overwriting"
    os.sys.exit(-2)
trunc_fh = open(trunc_family_file, 'w')
print >> trunc_fh, header.strip()

step = num_asteroids / num_req

ast_num = 0
orig_file_line_offset = 1+num_skip+1
while ast_num < num_asteroids:
    print "Looking at line", ast_num + orig_file_line_offset
    asteroid = asteroids[ast_num]
    # If there are more than 3 columns, it has WISE data so just write it out
    if len(asteroid.split()) > 3:
        print >> trunc_fh, asteroid
    else:
        # Search outward from starting point trying to find a better match with 
        # WISE data. Check we don't go off the end of the list
        offsets =  range(1, horizon+1)
        offsets.append(0)
        for offset in offsets:
            if ast_num - offset > 0:
                asteroid = asteroids[ast_num-offset]
                if len(asteroid.split()) > 3:
                    print "Found better match at line #=%d (offset=-%d)" % (ast_num-offset + orig_file_line_offset, offset)
                    break
            if ast_num + offset <= num_asteroids:
                asteroid = asteroids[ast_num+offset]
                if len(asteroid.split()) > 3:
                    print "Found better match at line #=%d (offset=+%d)" % (ast_num+offset + orig_file_line_offset, offset)
                    break
        if offset == 0:
            print "No better match found within horizon"           
        print >> trunc_fh, asteroid
    ast_num += step
trunc_fh.close()
