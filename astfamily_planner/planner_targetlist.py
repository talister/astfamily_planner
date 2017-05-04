#!/usr/bin/env python
import os
import json
from datetime import datetime, timedelta
from sys import exit
import numpy as np

import logging

from ephem_subs import call_compute_ephem, compute_ephem, determine_darkness_times, determine_exptime
from source_subs import submit_block_to_scheduler
from time_subs import datetime2mjd_utc

def read_elements_list(data_path, family):
    
    family_elements =  os.path.join(data_path, 'family_' + str(family) + '.elements')
    with open(family_elements, 'r') as f:
        bodies = json.load(f)

    return bodies

def determine_phaseangle_windows(obs_array, nsteps=10, dbg=True):

    index_max_phangle =  np.argmax(obs_array[:,1])
    if dbg: print "Max value of phaseangle = %4.1f at index %4d %s"  % ( np.amax(obs_array[:,1]), index_max_phangle, obs_array[index_max_phangle])
    
    index_min_phangle =  np.argmin(obs_array[:,1])
    if dbg: print "Min value of phaseangle = %4.1f at index %4d %s"  % ( np.amin(obs_array[:,1]), index_min_phangle, obs_array[index_min_phangle])

    phangle_range = obs_array[index_max_phangle][1] - obs_array[index_min_phangle][1]
    phangle_step = phangle_range / float(nsteps)
    if dbg: print "Range, steps of phaseangle= %.2f %.2f" % (phangle_range, phangle_step)

    phang_step = 0
    phang_windows = []
    while phang_step < nsteps:
        phang = obs_array[index_min_phangle][1] + phang_step * phangle_step
        phang_max = phang+(0.1*phangle_step)
        phang_min = phang-(0.1*phangle_step)
        if dbg: print "For phase angle %.1f->%.1f" % ( phang_min, phang_max)
        subset = obs_array[np.where((obs_array[:,1] >= phang_min) & (obs_array[:,1] <= phang_max))]
        if dbg: print subset
        if len(subset) > 0:
            phang_windows.append( [np.amin(subset[:,0]), np.amax(subset[:,0])] )
        phang_step += 1

    return phang_windows

def determine_params(exp_length, site_code, start_time, end_time, group_id):
    params = {'proposal_id': 'LCO2017AB-014',
              'user_id': 'tlister@lcogt.net',
              'tag_id': 'LCOGT',
              'priority': 15,
              'exp_count': 2,
              'exp_time': exp_length,
              'site_code':  site_code,
              'start_time': start_time,
              'end_time': end_time,
              'group_id': group_id,
              'filters' : 'rp, gp, ip, zs, rp'
              }
    return params

family = 'IR_NEOs'
data_path =  os.path.join('../', 'data')
sites = ['K92', 'W86', 'V37']
obs_start = datetime(2017,  5,  1, 0, 0, 0)
obs_end = datetime(2017, 11, 30, 23, 59, 59)
obs_step = '60m'
alt_limit = 30.0
mag_limit = 20.2
pixel_scale = 0.389
max_exptime = 300.0
nsteps = 4
submit = True

bodies = read_elements_list(data_path, family)
print "Read in ", len(bodies), "asteroids and elements."

logging.basicConfig(filename='planner_IR_NEOs_V2_faint.log', level=logging.INFO)

faint_objects = { 'W86' : [
                    '2006 NL',     # W86,   248
                    '426082',      # W86,   163
                    '2000 CE59',   # W86,    55
                    '2000 UW13',   # W86,    18
                    '288592',      # W86,   169
                    '2001 PT9',    # W86,   299
                    '2012 VO76',   # W86,    54
                    '2008 CC175',  # W86,    13
                    ],
            'V37' : [
                    '136582',      # V37,   323
                    '2012 XM145',  # V37,    70
                    '2011 TG2',    # V37,    79
                    '208023',      # V37,     4
                    '2000 CE59',   # V37,   560
                    '2004 QD14',   # V37,    28
                    '2000 UW13',   # V37,    10
                    '2012 VO76',   # V37,    86
                    '2008 CC175',  # V37,     8
                    '2007 DM41',   # V37,   184
                    ]
        }
faint_objects['K92'] = faint_objects['W86']

bright_objects = { 'W86': [
                    '162911',     #19.20, W86,   416
                    '458368',     #18.40, W86,   431
                    '152770',     #18.40, W86,   453
                    '162452',     #18.30, W86,   454
                    '2009 WO106', #19.10, W86,   464
                    '162117',     #19.10, W86,   476
                    '65679',      #19.40, W86,   494
                    '2014 SZ303', #18.10, W86,   502
                    '2004 BE68',  #18.40, W86,   507
                    '105141',     #18.90, W86,   512
                    '2009 QL8',   #19.50, W86,   515
                    '142464',     #18.10, W86,   519
                    '15817',      #18.50, W86,   528
                    '138911',     #19.20, W86,   545
                    '142561',     #18.10, W86,   607
                    '154268',     #18.00, W86,   622
                    '2003 WR21',  #19.60, W86,   659
                    '136818',     #18.90, W86,   675
                    '333478',     #18.20, W86,   689
                    '2007 AS12',  #19.10, W86,   722
                    '141018',     #18.90, W86,   732
                    '2009 KN4',   #18.30, W86,   745
                    '159467',     #18.20, W86,   919
                    '137799',     #18.50, W86,   948
                    '96631',      #18.10, W86,  1065
                    ],
            'V37' : [
                    '441825',     #18.50, V37,  1083
                    '55408',      #18.60, V37,   752
                    '96631',      #18.10, V37,   798
                    '1999 HY1',   #18.10, V37,   806
                    '142561',     #18.10, V37,   822
                    '142464',     #18.10, V37,   934
                    '162472',     #19.10, V37,   681
                    '203015',     #18.40, V37,   686
                    '2009 WO106', #19.10, V37,   522
                    '159467',     #18.20, V37,   525
                    '415715',     #18.20, V37,   531
                    '136818',     #18.90, V37,   574
                    '65679',      #19.40, V37,   590
                    '329520',     #19.80, V37,   595
                    '2004 BE68',  #18.40, V37,   625
                    '438017',     #18.70, V37,   507
                    '2002 UA31',  #19.00, V37,   460
                    '2001 QD96',  #18.20, V37,   470
                    '137799',     #18.50, V37,   487
                    '138911',     #19.20, V37,   496
                    '15817',      #18.50, V37,   422
                    ]
    }
bright_objects['K92'] = bright_objects['W86']
objects = bright_objects
#objects = faint_objects

for site in objects.keys():
    print "Site: ", site, objects[site]
#exit(0)

line_fmt = "%s    %s %s    %s    %s   %3s   %3s  %4s %s  %5.1f"
for asteroid in bodies:
    ast_name = str(asteroid.keys()[0])
    for site in sites:
        if ast_name in objects[site]:
            print "Matched %s at %s" % ( ast_name, site )
            ast_file = os.path.join(data_path, ast_name.replace(' ', '') + '_' + site + '_output')
            ast_fh = open(ast_file, 'w')
            num_written = 0
            ast_elems = asteroid.values()[0]
            ast_elems['current_name'] = ast_name
    # Compute epoch of the elements as a MJD
            try:
                epochofel = datetime.strptime(ast_elems['epochofel'], '%Y-%m-%d %H:%M:%S')
            except TypeError:
                epochofel = ast_elems['epochofel']
            epoch_mjd = datetime2mjd_utc(epochofel)
            ast_elems['epochofel_mjd'] = epoch_mjd

            msg =  "Working on %s at %s" % ( ast_name, site)
            logging.info(msg)
            print >> ast_fh, "# %s  (H=%2.1f) at %s" % ( ast_name, ast_elems['abs_mag'], site )
            print >> ast_fh, "#UTC date/time          RA (J2000.0) Dec     PhaseA    Vmag   Alt MoonD Score  H.A. Exptime"

            d = obs_start
            first_row = True
            while d <= obs_end:
                dark_start, dark_end = determine_darkness_times(site, d)
                emp = call_compute_ephem(ast_elems, dark_start, dark_end, site, obs_step, alt_limit, mag_limit)
                if len(emp) > 0:
                    for line in emp:
        # 0         1  2   3          4    5    6   7           8        9      10   11
        # datetime RA Dec PhaseAngle Mag Speed  Alt MoonPhase MoonDist MoonAlt Score HA
                        exptime = determine_exptime(float(line[5]), pixel_scale, max_exptime)
                        print >> ast_fh, line_fmt % (line[0], line[1], line[2], line[3], line[4], line[6], line[8], line[10], line[11], exptime)
                        newrow = [datetime.strptime(line[0], "%Y %m %d %H:%M"), float(line[3]), float(line[4]), float(line[5]), float(line[8]), float(line[10])]
                        if first_row:
                            obs_array = np.array(newrow)
                            first_row = False
                        else:
                            obs_array = np.vstack([obs_array, newrow])
                        num_written += 1
                d = d + timedelta(days=1)

            ast_fh.close()
            if num_written < nsteps:
                lines_msg, file_msg = ("Not enough", "")
                if num_written == 0:
                    lines_msg, file_msg = ("No", "empty")
                logging.warn("%s lines of output produced for %s. Removing %s output file %s." % (lines_msg, ast_name, file_msg, ast_file))
                os.remove(ast_file)
            else:
                phang_windows = determine_phaseangle_windows(obs_array, nsteps, True)
                window = 0
                msg =  "Scheduling %d windows for %s at %s" % (  len(phang_windows), ast_name, site)
                logging.info(msg)
                while window < len(phang_windows):
                    # Refine windows
                    dark_start, dark_end = determine_darkness_times(site, phang_windows[window][0])
                    window_start = dark_start
                    dark_start, dark_end = determine_darkness_times(site, phang_windows[window][1])
                    window_end = dark_end

                    if window_start != window_end and window_end > datetime.utcnow():
                        subset = obs_array[np.where((obs_array[:,0] >= window_start) & (obs_array[:,0] <= window_end))]
                        mean_speed = np.mean(subset[:,3])
                        mean_mag = np.mean(subset[:,2])
                        exptime = determine_exptime(mean_speed, pixel_scale, max_exptime)
                        group_id = ast_name + "_" + site + '_phasea#' + str(window+1)
                        logging.info("Window #%2d (%s->%s), speed=%.1f, mag=%.1f, exptime=%.1f secs" % ( window, window_start, window_end, mean_speed, mean_mag, exptime))
                        params = determine_params(exptime, site, window_start, window_end, group_id)
                        if submit:
                            tracking_number, resp_params = submit_block_to_scheduler(ast_elems, params)
                        else:
                            print params
                    window += 1
