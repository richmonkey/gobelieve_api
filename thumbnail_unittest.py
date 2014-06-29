import unittest
from thumbnail import *


class TestThumbnail(unittest.TestCase):
    def setUp(self):
        pass

    def test_thumbnail_path(self):
        path = "/images/4471ec197e0822704d23bcdf933a4412.jpg@128w_128h_1c.jpg"
        self.assertTrue(is_thumbnail(path))
        tb_path = thumbnail_path(path)
        self.assertEqual(tb_path, "/images/4471ec197e0822704d23bcdf933a4412_128w_128h_1c.jpg")
        
    def test_thumbnail_short_path(self):
        path = "4471ec197e0822704d23bcdf933a4412.jpg@128w_128h_1c.jpg"
        self.assertTrue(is_thumbnail(path))
        tb_path = thumbnail_path(path)
        self.assertEqual(tb_path, "4471ec197e0822704d23bcdf933a4412_128w_128h_1c.jpg")
