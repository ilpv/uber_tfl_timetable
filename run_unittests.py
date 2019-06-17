import unittest
import database_shard
import time

class Test(unittest.TestCase):
     
    @classmethod
    def setUpClass(cls):
        database_shard.init()

    @classmethod
    def tearDownClass(cls):
        database_shard.destroy()

    def test_getTimeTable(self):
        res = database_shard.getTimeTable(51.510500,-0.118444,"490020255S")
        self.assertTrue(res)
        self.assertFalse(res["Error"])
        self.assertTrue(res["Data"])
        for x in res["Data"]:
            self.assertTrue(x['timeToStation']>0)

    def test_getNearestStops(self):
        res = database_shard.getNearestStops(51.509700,-0.123193)
        self.assertTrue(res)
        for x in res:
            # Check Stop's coordinates within bounds
            self.assertTrue(x['lat']>database_shard.Xlow)
            self.assertTrue(x['lat']<database_shard.Xhigh)
            self.assertTrue(x['lon']>database_shard.Ylow)
            self.assertTrue(x['lon']<database_shard.Yhigh)

    def test_getOutofBoundsStops(self):
        res = database_shard.getNearestStops(55.751244,37.618423)
        self.assertFalse(res)

    def test_CheckTimeTableCached(self):
        start = time.time()
        res1 = database_shard.getTimeTable(51.510500,-0.118935,"490008932T")
        res2 = database_shard.getTimeTable(51.510500,-0.118935,"490008932T")
        res3 = database_shard.getTimeTable(51.510500,-0.118935,"490008932T")
        end = time.time()
        self.assertTrue(res1)
        self.assertTrue(res2)
        self.assertTrue(res3)
        if start - end < database_shard.diff_time_sec:
            #Compare data
            eqs12 = {i: res1[i] for i in res1 if i in res2 and res1[i] != res2[i]}
            self.assertTrue(len(eqs12))
            eqs23 = {i: res2[i] for i in res2 if i in res3 and res2[i] != res3[i]}
            self.assertFalse(len(eqs23))

if __name__ == "__main__":
    unittest.main()
