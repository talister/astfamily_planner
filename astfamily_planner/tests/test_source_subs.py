import unittest

from astfamily_planner.source_subs import split_asteroid, split_trilling_targets

class TestNameSplitter(unittest.TestCase):

    def test_small_number(self):
        asteroid = '566'

        expected = '00566'

        result = split_asteroid(asteroid)

        self.assertEqual(expected, result)

    def test_mid_number(self):
        asteroid = '6962'

        expected = '06962'

        result = split_asteroid(asteroid)

        self.assertEqual(expected, result)

    def test_big_number(self):
        asteroid = '79620'

        expected = '79620'

        result = split_asteroid(asteroid)

        self.assertEqual(expected, result)

    def test_desig1(self):
        asteroid = '2005QX76'

        expected = '2005 QX76'

        result = split_asteroid(asteroid)

        self.assertEqual(expected, result)

    def test_desig2(self):
        asteroid = '2005QX'

        expected = '2005 QX'

        result = split_asteroid(asteroid)

        self.assertEqual(expected, result)

    def test_desig3(self):
        asteroid = '2007VN312'

        expected = '2007 VN312'

        result = split_asteroid(asteroid)

        self.assertEqual(expected, result)

    def test_desig4(self):
        asteroid = '2007 VN312'

        expected = '2007 VN312'

        result = split_asteroid(asteroid)

        self.assertEqual(expected, result)

class TestSplitTrillingTargets(unittest.TestCase):

    def test_number_name_desig(self):
        asteroid = '1917_Cuyo_1968_AA'

        expected = ('1917', '1968 AA')

        result = split_trilling_targets(asteroid)

        self.assertEqual(expected, result)

    def test_number_name_desig2(self):
        asteroid = '1980_Tezcatlipoca_1950'

        expected = ('1980', '')

        result = split_trilling_targets(asteroid)

        self.assertEqual(expected, result)

    def test_number_noname_desig(self):
        asteroid = '5626_1991_FE'

        expected = ('5626', '1991 FE')

        result = split_trilling_targets(asteroid)

        self.assertEqual(expected, result)

    def test_number_noname_desig2(self):
        asteroid = '276891_2004_RH340'

        expected = ('276891', '2004 RH340')

        result = split_trilling_targets(asteroid)

        self.assertEqual(expected, result)

    def test_temp_desig(self):
        asteroid = '2016_LH49'

        expected = ('', '2016 LH49')

        result = split_trilling_targets(asteroid)

        self.assertEqual(expected, result)

    def test_survey_desig(self):
        asteroid = '6344_P-L'

        expected = ('', '6344 P-L')

        result = split_trilling_targets(asteroid)

        self.assertEqual(expected, result)
