"""Diff two MARC records from given input files."""
import logging
from pymarc import parse_xml_to_array
import sys


def read_marc(filename):
    """Read MARC record from filename.

    Takes just the first record if there are multiple ones.
    """
    logging.info("Reading %s" % (filename))
    records = parse_xml_to_array(filename)
    if (len(records) == 0):
        logging.error("No records in %s, aborting" % (filename))
        raise Exception("No records in %s, aborting" % (filename))
    elif (len(records) > 1):
        logging.info("Have taken first of %d records from %s" % (len(records), filename))
    return(records[0])


def marc_diff(m1, m2, verbose=False, ignore=[]):
    """Diff two MARC records, m1 and m2, to fh.

    Ignore fields with tag values (string or int) in ignore.

    Write out lines:
      == - equal (only if verbose)
      -< - different, m1 version
      -> - different, m2 version
      << - only in m1
      >> - only in m2

    FIXME - need to flesh out more sensible handling of differences
    in cases where there are fifferent numbers of fields with same tag,
    or differences in subfields within same tag.
    """
    ignore = [int(i) for i in ignore]  # '001' -> 1 etc.
    m1 = iter(m1)
    m2 = iter(m2)
    f1 = next(m1, None)
    f2 = next(m2, None)
    diff = []
    while (f1 or f2):
        if (f1 is not None and f2 is not None and f1.tag == f2.tag):
            if (str(f1) != str(f2) and int(f1.tag) not in ignore):
                diff.append('-< %s' % (str(f1)))
                diff.append('-> %s' % (str(f2)))
            elif (verbose):
                diff.append('== %s' % (str(f1)))
            f1 = next(m1, None)
            f2 = next(m2, None)
        elif (f1 is None or (f2 is not None and f1.tag > f2.tag)):
            if (int(f2.tag) not in ignore):
                diff.append('>> %s' % (str(f2)))
            f2 = next(m2, None)
        elif (f2 is None or f1.tag < f2.tag):
            if (int(f1.tag) not in ignore):
                diff.append('<< %s' % (str(f1)))
            f1 = next(m1, None)
    return('\n'.join(diff))
