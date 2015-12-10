import unittest

from astfamily_planner.source_subs import split_asteroid

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
