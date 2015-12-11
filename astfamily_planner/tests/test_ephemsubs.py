import unittest
from datetime import datetime

from astfamily_planner.ephem_subs import compute_ephem, call_compute_ephem

class TestComputeEphem(unittest.TestCase):

    def setUp(self):
        self.elements = { u'abs_mag': 9.56,
                          u'active': True,
                          u'arc_length': 39487,
                          u'argofperih': 177.40017,
                          u'discovery_date': u'1907-09-06 00:00:00',
                          u'eccentricity': 0.1028177,
                          u'elements_type': u'MPC_MINOR_PLANET',
                          u'epochofel': u'2016-01-13 00:00:00',
                          u'longascnode': 286.13355,
                          u'meananom': 250.15749,
                          u'meandist': 2.4648879,
                          u'not_seen': 54.97520113715278,
                          u'num_obs': 1101,
                          u'orbinc': 5.2401,
                          u'origin': u'M',
                          u'slope': 0.15,
                          u'update_time': u'2015-10-17 00:00:00',
                          u'updated': True}

    def test_ephem_566_K91_Dec102015(self):
    
        site = 'K91'
        ephem_start = datetime(2015, 12, 10, 18, 0, 0)
    
#        expected = ['2015 12 10 18:00', '21 11 39.20', '-12 34 06.3',   58.5  18.8  15.0    0.89    072.8    100  +39   -05   0.00   066  -15]

        expected = (ephem_start, 5.5486346615349067, -0.21936045307765661, 14.970369998574069, 0.89322757180821588, 38.574338332084082, 77.430833333333339, 0.327653760271 )

        emp = compute_ephem(ephem_start, self.elements, site, False, True, False)

        self.assertEqual(expected, emp)

class TestCallComputeEphem(unittest.TestCase):

    def setUp(self):
        self.elements = { u'abs_mag': 9.56,
                          u'active': True,
                          u'arc_length': 39487,
                          u'argofperih': 177.40017,
                          u'discovery_date': u'1907-09-06 00:00:00',
                          u'eccentricity': 0.1028177,
                          u'elements_type': u'MPC_MINOR_PLANET',
                          u'epochofel': u'2016-01-13 00:00:00',
                          u'longascnode': 286.13355,
                          u'meananom': 250.15749,
                          u'meandist': 2.4648879,
                          u'not_seen': 54.97520113715278,
                          u'num_obs': 1101,
                          u'orbinc': 5.2401,
                          u'origin': u'M',
                          u'slope': 0.15,
                          u'update_time': u'2015-10-17 00:00:00',
                          u'updated': True}
        self.ephem_step = '60m'
        self.alt_limit = 30

    def test_ephem_566_K91_Dec2015(self):
    
        site = 'K91'
        ephem_start = datetime(2015, 12, 10, 18, 0, 0)
        ephem_end = datetime(2015, 12, 11, 2, 0, 0)
    
#        expected = ['2015 12 10 18:00', '21 11 39.20', '-12 34 06.3',   58.5  18.8  15.0    0.89    072.8    100  +39   -05   0.00   066  -15]
        expected = [['2015 12 10 18:00', '21 11 39.20', '-12 34 06.3', '15.0', ' 0.89', '+38', '0.01', ' 66', '-15', '+043', '+03:27']]

        emp = call_compute_ephem(self.elements, ephem_start, ephem_end, site, self.ephem_step, self.alt_limit)


        self.assertEqual(expected, emp)


    def test_ephem_566_K91_Oct2015(self):
    
        site = 'K91'
        ephem_start = datetime(2015, 10, 10, 18, 0, 0)
        ephem_end = datetime(2015, 10, 11, 2, 0, 0)
    
#        expected = [[2015 10 10 180000 20 06 39.0 -16 32 38   2.238   2.653  103.4  21.5  14.5    0.33    078.1    153  +73   -16   0.04   128  -40       N/A   N/A / Map / Offsets
#2015 10 10 190000 20 06 40.4 -16 32 34   2.238   2.653  103.3  21.5  14.5    0.33    078.0    121  +64   -28   0.04   127  -50       N/A   N/A / Map / Offsets
#2015 10 10 200000 20 06 41.8 -16 32 29   2.239   2.653  103.3  21.5  14.5    0.34    077.9    105  +52   -38   0.04   127  -57       N/A   N/A / Map / Offsets
#2015 10 10 210000 20 06 43.1 -16 32 25   2.239   2.653  103.2  21.5  14.5    0.34    077.9    095  +40   -46   0.04   126  -60       N/A   N/A / Map / Offsets'''

        expected = [['2015 10 10 18:00', '20 06 38.62', '-16 32 38.9', '14.5', ' 0.33', '+72', '0.05', '128', '-40', '+085', '+00:31'],
                    ['2015 10 10 19:00', '20 06 39.98', '-16 32 34.8', '14.5', ' 0.33', '+63', '0.04', '127', '-50', '+080', '+01:31'],
                    ['2015 10 10 20:00', '20 06 41.35', '-16 32 30.6', '14.5', ' 0.34', '+52', '0.04', '126', '-57', '+070', '+02:32'],
                    ['2015 10 10 21:00', '20 06 42.72', '-16 32 26.3', '14.5', ' 0.34', '+39', '0.04', '126', '-59', '+059', '+03:32'],
                   ]

        emp = call_compute_ephem(self.elements, ephem_start, ephem_end, site, self.ephem_step, self.alt_limit)

        self.assertEqual(len(expected), len(emp))
        i = 0
        while i < len(expected):
            self.assertEqual(expected[i], emp[i])
            i+=1
