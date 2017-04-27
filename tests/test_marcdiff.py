import unittest
from pymarc import Record, Field
from mdmux.marcdiff import read_marc, marc_diff


class TestMarcdiff(unittest.TestCase):

    def test01_read_marc(self):
        # zero records
        self.assertRaises(Exception, read_marc, 'testdata/marc_0_records.xml')
        # first of three records
        r = read_marc('testdata/marc_3_records.xml')
        self.assertEqual(r[1], 'test1')

    def test02_marc_diff(self):
        m1 = Record()
        m1.add_field(Field(tag='001', data='abc'))
        m2 = Record()
        m2.add_field(Field(tag='001', data='abc'))
        diff = marc_diff(m1, m2)
        self.assertEqual(diff, '')
        diff = marc_diff(m1, m2, verbose=True)
        self.assertEqual(diff, '== =001  abc')
        m1.add_field(Field(tag='002', data='def'))
        m2.add_field(Field(tag='002', data='ghi'))
        diff = marc_diff(m1, m2)
        self.assertEqual(diff, '-< =002  def\n-> =002  ghi')
        diff = marc_diff(m1, m2, ignore=[2])
        self.assertEqual(diff, '')
        diff = marc_diff(m1, m2, ignore=['002'])
        self.assertEqual(diff, '')
        m1.add_field(Field(tag='003', data='three'))
        m2.add_field(Field(tag='004', data='four'))
        diff = marc_diff(m1, m2, ignore=['002'])
        self.assertEqual(diff, '<< =003  three\n>> =004  four')
        diff = marc_diff(m1, m2, ignore=[2, 4])
        self.assertEqual(diff, '<< =003  three')
        diff = marc_diff(m1, m2, ignore=[2, 3])
        self.assertEqual(diff, '>> =004  four')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMarcdiff)
    unittest.TextTestRunner().run(suite)
