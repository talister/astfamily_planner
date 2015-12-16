import logging
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup
from re import sub

from reqdb.client import SchedulerClient
from reqdb.requests import Request, UserRequest

from time_subs import extract_mpc_epoch

logger = logging.getLogger(__name__)

def clean_NEOCP_object(page_list):
    '''Parse response from the MPC NEOCP page making sure we only return
    parameters from the 'NEOCPNomin' (nominal orbit)'''
    current = False
    if page_list[0] == '':
        page_list.pop(0)
    if page_list[0][:6] == 'Object':
        page_list.pop(0)
    for line in page_list:
        if 'NEOCPNomin' or 'MPCLINUX' in line:
            current = line.strip().split()
            break
    if current:
        print len(current)
        if len(current) == 16:
            # Missing H parameter, probably...
            try:
                slope = float(current[2])
                # ...nope guess again... Could be missing RMS...
                try:
                    rms = float(current[15])
                except ValueError:
                     # Insert a high value for the missing rms
                    current.insert(15, 99.99)
                    logger.warn(
                        "Missing RMS for %s; assuming 99.99", current[0])
                except:
                    logger.error(
                        "Missing field in NEOCP orbit for %s which wasn't correctable", current[0])
            except ValueError:
                # Insert a high magnitude for the missing H
                current.insert(1, 99.99)
                logger.warn(
                    "Missing H magnitude for %s; assuming 99.99", current[0])
            except:
                logger.error(
                    "Missing field in NEOCP orbit for %s which wasn't correctable", current[0])

        if len(current) == 17:
            params = {
                'abs_mag': float(current[1]),
                'slope': float(current[2]),
                'epochofel': extract_mpc_epoch(current[3]),
                'meananom': float(current[4]),
                'argofperih': float(current[5]),
                'longascnode': float(current[6]),
                'orbinc': float(current[7]),
                'eccentricity': float(current[8]),
                'meandist': float(current[10]),
                'source_type': 'U',
                'elements_type': 'MPC_MINOR_PLANET',
                'active': True,
                'origin': 'M',
                'update_time' : datetime.utcnow()
            }
        elif len(current) == 22 or len(current) == 24:
            params = {
                'abs_mag': float(current[1]),
                'slope': float(current[2]),
                'epochofel': extract_mpc_epoch(current[3]),
                'meananom': float(current[4]),
                'argofperih': float(current[5]),
                'longascnode': float(current[6]),
                'orbinc': float(current[7]),
                'eccentricity': float(current[8]),
                'meandist': float(current[10]),
                'source_type': 'U',
                'elements_type': 'MPC_MINOR_PLANET',
                'active': True,
                'origin': 'M',
                'provisional_name' : current[0],
                'num_obs' : int(current[13]),
                'update_time' : datetime.utcnow(),
                'arc_length' : None,
                'not_seen' : None
            }
            # If this is a find_orb produced orbit, try and fill in the
            # 'arc length' and 'not seen' values.
            arc_length = None
            arc_units = current[16]
            if arc_units == 'days':
                arc_length = float(current[15])
            elif arc_units == 'hrs':
                arc_length = float(current[15]) / 24.0
            elif arc_units == 'min':
                arc_length = float(current[15]) / 1440.0
            if arc_length:
                params['arc_length'] = arc_length
            try:
                not_seen = datetime.utcnow() - datetime.strptime(current[-1], '%Y%m%d')
                params['not_seen'] = not_seen.total_seconds() / 86400.0 # Leap seconds can go to hell...
            except:
                pass
        else:
            logger.warn(
                "Did not get right number of parameters for %s. Values %s", current[0], current)
            params = {}
    else:
        params = {}
    return params


def fetchpage_and_make_soup(url, fakeagent=False, dbg=False, parser="html.parser"):
    '''Fetches the specified URL from <url> and parses it using BeautifulSoup.
    If [fakeagent] is set to True, we will pretend to be a Firefox browser on
    Linux rather than as Python-urllib (in case of anti-machine filtering).
    If [parser] is specified, try and use that BeautifulSoup parser (which
    needs to be installed). Defaults to "html.parser" if not specified; may need
    to use "html5lib" to properly parse malformed MPC pages.

    Returns the page as a BeautifulSoup object if all was OK or None if the
    page retrieval failed.'''

    req_headers = {}
    if fakeagent == True:
        req_headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0",
                      }
    req_page = urllib2.Request(url, headers=req_headers)
    opener = urllib2.build_opener() # create an opener object
    try:
        response = opener.open(req_page)
    except urllib2.URLError as e:
        if not hasattr(e, "code"):
            raise
        print "Page retrieval failed:", e
        return None

  # Suck the HTML down
    neo_page = response.read()

# Parse into beautiful soup
    page = BeautifulSoup(neo_page, parser)

    return page

def clean_element(element):
    '''Cleans an element (passed) by converting to ascii and removing any units'''
    key = element[0].encode('ascii', 'ignore')
    value = element[1].encode('ascii', 'ignore')
    # Match a open parenthesis followed by 0 or more non-whitespace followed by
    # a close parenthesis and replace it with a blank string
    key = sub(r' \(\S*\)','', key)

    return (key, value)


def fetch_mpcdb_page(asteroid, dbg=False):
    '''Performs a search on the MPC Database for <asteroid> and returns a
    BeautifulSoup object of the page (for future use by parse_mpcorbit())'''

    #Strip off any leading or trailing space and replace internal space with a
    # plus sign
    if dbg: print "Asteroid before=", asteroid
    asteroid = asteroid.strip().replace(' ', '+')
    if dbg: print "Asteroid  after=", asteroid
    query_url = 'http://www.minorplanetcenter.net/db_search/show_object?object_id=' + asteroid

    page = fetchpage_and_make_soup(query_url)
    if page == None:
        return None

#    if dbg: print page
    return page

def parse_mpcorbit(page, dbg=False):

    data = []
    # Find the table of elements and then the subtables within it
    elements_table = page.find('table', {'class' : 'nb'})
    if elements_table == None:
        if dbg: "No element tables found"
        return None
    data_tables = elements_table.find_all('table')
    for table in data_tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [elem.text.strip() for elem in cols]
            data.append([elem for elem in cols if elem])

    elements = dict(clean_element(elem) for elem in data)

    name_element = page.find('h3')
    if name_element != None:
        elements['obj_id'] = name_element.text.strip()

    return elements


def clean_mpcorbit(elements, dbg=False, origin='M'):
    '''Takes a list of (proto) element lines from fetch_mpcorbit() and plucks
    out the appropriate bits. origin defaults to 'M'(PC) if not specified'''

    params = {}
    if elements != None:

        try:
            last_obs = datetime.strptime(elements['last observation date used'].replace('.0', ''), '%Y-%m-%d')
        except ValueError:
            last_obs = None

        try:
            first_obs = datetime.strptime(elements['first observation date used'].replace('.0', ''), '%Y-%m-%d')
        except ValueError:
            first_obs = None

        params = {
            'epochofel'     : datetime.strptime(elements['epoch'].replace('.0', ''), '%Y-%m-%d'),
            'abs_mag'       : float(elements['absolute magnitude']),
            'slope'         : float(elements['phase slope']),
            'meananom'      : float(elements['mean anomaly']),
            'argofperih'    : float(elements['argument of perihelion']),
            'longascnode'   : float(elements['ascending node']),
            'orbinc'        : float(elements['inclination']),
            'eccentricity'  : float(elements['eccentricity']),
            'meandist'      : float(elements['semimajor axis']),
#            'source_type': determine_asteroid_type(float(elements['perihelion distance']), float(elements['eccentricity'])),
            'elements_type' : 'MPC_MINOR_PLANET',
            'active'        : True,
            'origin'        : origin,
            'updated'       : True,
            'num_obs'       : int(elements['observations used']),
            'arc_length'    : int(elements['arc length']),
            'discovery_date' : first_obs,
            'update_time'   : last_obs
        }

        not_seen = None
        if last_obs != None:
            time_diff = datetime.utcnow() - last_obs
            not_seen = time_diff.total_seconds() / 86400.0
        params['not_seen'] = not_seen
    return params


def update_MPC_orbit(obj_id_or_page, dbg=False, origin='M'):
    '''
    Performs remote look up of orbital elements for object with id obj_id_or_page,
    Gets or creates corresponding Body instance and updates entry.
    Alternatively obj_id_or_page can be a BeautifulSoup object, in which case
    the call to fetch_mpcdb_page() will be skipped and the passed BeautifulSoup
    object will parsed.
    '''

    if type(obj_id_or_page) != BeautifulSoup:
        obj_id = obj_id_or_page
        page = fetch_mpcdb_page(obj_id, dbg)

        if page == None:
            logger.warn("Could not find elements for %s" % obj_id)
            return False
    else:
        page = obj_id_or_page

    elements = parse_mpcorbit(page, dbg)
    if type(obj_id_or_page) == BeautifulSoup:
        obj_id = elements['obj_id']
        del elements['obj_id']

    cleaned_elements = clean_mpcorbit(elements, dbg, origin)

    return cleaned_elements
    
def split_asteroid(asteroid):
    '''Splits names of the form '2014PD25' into '2014 PD25' and zeropads too 
    short numbers e.g. (63) -> 00063 for use with the MPC service (e.g. via
    update_mpc_orbit() or for looking up in the downloaded MPCOrb.dat'''

    if len(asteroid) > 5:
        if asteroid[0:4].isdigit() and asteroid[5].isalpha():
            asteroid = asteroid[0:4] + ' ' + asteroid[4:].strip()
    else:
        if asteroid.isdigit():
            asteroid = "%05d" % int(asteroid)

    return asteroid

def make_location(params):
    location = {
        'telescope_class' : params['pondtelescope'][0:3],
        'site'        : params['site'].lower(),
        'observatory' : params['observatory'],
        'telescope'   : '',
    }

# Check if the 'pondtelescope' is length 4 (1m0a) rather than length 3, and if
# so, update the null string set above with a proper telescope
    if len(params['pondtelescope']) == 4:
        location['telescope'] = params['pondtelescope']

    return location

def make_target(params):
    '''Make a target dictionary for the request. RA and Dec need to be
    decimal degrees'''

    ra_degs = math.degrees(params['ra_rad'])
    dec_degs = math.degrees(params['dec_rad'])
    target = {
               'name' : params['source_id'],
               'ra'   : ra_degs,
               'dec'  : dec_degs
             }
    return target

def make_moving_target(elements):
    '''Make a target dictionary for the request from an element set'''

    print elements
    # Generate initial dictionary of things in common
    target = {
                  'name'                : elements['current_name'],
                  'type'                : 'NON_SIDEREAL',
                  'scheme'              : elements['elements_type'],
                  # Moving object param
                  'epochofel'         : elements['epochofel_mjd'],
                  'orbinc'            : elements['orbinc'],
                  'longascnode'       : elements['longascnode'],
                  'argofperih'        : elements['argofperih'],
                  'eccentricity'      : elements['eccentricity'],
            }

    if elements['elements_type'].upper() == 'MPC_COMET':
        target['epochofperih'] = elements['epochofperih']
        target['perihdist'] = elements['perihdist']
    else:
        target['meandist']  = elements['meandist']
        target['meananom']  = elements['meananom']

    return target

def make_window(params):
    '''Make a window. This is simply set to the start and end time from
    params (i.e. the picked time with the best score plus the block length),
    formatted into a string.
    Hopefully this will prevent rescheduling at a different time as the
    co-ords will be wrong in that case...'''
    window = {
              'start' : params['start_time'].strftime('%Y-%m-%dT%H:%M:%S'),
              'end'   : params['end_time'].strftime('%Y-%m-%dT%H:%M:%S'),
             }

    return window

def make_molecule(params):
    molecule = {
                'exposure_count'  : params['exp_count'],
                'exposure_time' : params['exp_time'],
                'bin_x'       : params['binning'],
                'bin_y'       : params['binning'],
                'instrument_name'   : params['instrument'],
                'filter'      : params['filter'],
                'ag_mode'     : 'Optional', # 0=On, 1=Off, 2=Optional.  Default is 2.
                'ag_name'     : ''

    }
    return molecule

def make_proposal(params):
    '''Construct needed proposal info'''

    proposal = {
                 'proposal_id'   : params['proposal_id'],
                 'user_id'       : params['user_id'],
                 'tag_id'        : params['tag_id'],
                 'priority'      : params['priority'],
               }
    return proposal

def make_constraints(params):
    constraints = {
                      'max_airmass' : 2.0,    # 30 deg altitude (The maximum airmass you are willing to accept)
#                       'max_airmass' : 1.74,   # 35 deg altitude (The maximum airmass you are willing to accept)
#                      'max_airmass' : 1.55,   # 40 deg altitude (The maximum airmass you are willing to accept)
#                      'max_airmass' : 2.37,    # 25 deg altitude (The maximum airmass you are willing to accept)
                    }
    return constraints    
def configure_defaults(params):

    site_list = { 'V37' : 'ELP' , 'K92' : 'CPT', 'Q63' : 'COJ', 'W85' : 'LSC', 'W86' : 'LSC', 'F65' : 'OGG', 'E10' : 'COJ' }
    params['pondtelescope'] = '1m0'
    params['observatory'] = ''
    params['site'] = site_list[params['site_code']]
    params['binning'] = 2
    params['instrument'] = '1M0-SCICAM-SBIG'
    params['filter'] = 'w'

    if params['site_code'] == 'W86' or params['site_code'] == 'W87':
        params['binning'] = 1
#        params['observatory'] = 'domb'
        params['instrument'] = '1M0-SCICAM-SINISTRO'
    elif params['site_code'] == 'F65' or params['site_code'] == 'E10':
        params['instrument'] =  '2M0-SCICAM-SPECTRAL'
        params['pondtelescope'] = '2m0'
        params['filter'] = 'solar'

    return params

def submit_block_to_scheduler(elements, params):
    request = Request()

    params = configure_defaults(params)
# Create Location (site, observatory etc) and add to Request
    location = make_location(params)
    logger.debug("Location=%s" % location)
    request.set_location(location)
# Create Target (pointing) and add to Request
    if len(elements) > 0:
        logger.debug("Making a moving object")
        target = make_moving_target(elements)
    else:
        logger.debug("Making a static object")
        target = make_target(params)
    logger.debug("Target=%s" % target)
    request.set_target(target)
# Create Window and add to Request
    window = make_window(params)
    logger.debug("Window=%s" % window)
    request.add_window(window)
# Create Molecule and add to Request
    params['filter'] = 'V'
    molecule_V = make_molecule(params)
    params['filter'] = 'I'
    molecule_I = make_molecule(params)
    request.add_molecule(molecule_V) # add exposure to the request
    request.add_molecule(molecule_I) # add exposure to the request

    request.set_note('Submitted by planner')
    logger.debug("Request=%s" % request)

    constraints = make_constraints(params)
    request.set_constraints(constraints)

# Add the Request to the outer User Request
    user_request =  UserRequest(group_id=params['group_id'])
    user_request.add_request(request)
    user_request.operator = 'single'
    proposal = make_proposal(params)
    user_request.set_proposal(proposal)

# Make an endpoint and submit the thing
    client = SchedulerClient('http://scheduler1.lco.gtn/requestdb/')
    response_data = client.submit(user_request)
    client.print_submit_response()
    request_numbers =  response_data.get('request_numbers', '')
    tracking_number =  response_data.get('tracking_number', '')
#    request_numbers = (-42,)
    if not tracking_number or not request_numbers:
        logger.error("No Tracking/Request number received")
        return False, params
    request_number = request_numbers[0]
    logger.info("Tracking, Req number=%s, %s" % (tracking_number,request_number))

    return tracking_number, params
