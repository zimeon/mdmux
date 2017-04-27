import unittest
from mdmux.bf2marc import Converter
from mdmux.marcdiff import read_marc, marc_diff
from tempfile import NamedTemporaryFile


class TestConverter(unittest.TestCase):

    def test01_init(self):
        c = Converter()
        self.assertFalse(c.dump_json)
        c = Converter(dump_json=True)
        self.assertTrue(c.dump_json)

    def test02_convert(self):
        c = Converter()
        xml = c.convert('testdata/102063.min.ttl')
        with NamedTemporaryFile('w', delete=False) as fh:
            fh.write(xml)
            fh.close()
            m1 = read_marc('testdata/102063.min.xml')
            m2 = read_marc(fh.name)
            self.assertEqual(marc_diff(m1, m2, ignore=[1,8]), '')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConverter)
    unittest.TextTestRunner().run(suite)
