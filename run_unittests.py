import unittest
import tfl_api

class Test(unittest.TestCase):

    def test_getTimeTable(self):
        res = tfl_api.getTimeTable("490020255S")
        self.assertTrue(res)
        for x in res["Data"]:
            self.assertTrue(x['timeToStation']>0)

    def test_getNearesStops(self):
        res = tfl_api.getNearestStops(51.50986,-0.118092)
        self.assertTrue(res)
        for x in res["Data"]["stopPoints"]:
            # Check Stop's coordinates within bounds
            self.assertTrue(x['lat']>-180)
            self.assertTrue(x['lat']<180)
            self.assertTrue(x['lon']>-180)
            self.assertTrue(x['lon']<180)

if __name__ == "__main__":
    unittest.main()
