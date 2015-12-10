import logging
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup
from re import sub

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
