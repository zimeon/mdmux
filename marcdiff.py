#!/usr/bin/env python
"""Diff two MARC records from given input files."""
import logging
import optparse
from pymarc import parse_xml_to_array
import sys


def read_marc(filename):
    """Read MARC record from filename."""
    logging.info("Reading %s" % (filename))
    records = parse_xml_to_array(filename)
    if (len(records) == 0):
        logging.error("No records in %s, aborting" % (filename))
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

    FIXME - need to flesh out more subtle handling of differences
    in cases with different numbers of fields with same tag, or differences
    in subfields within same tag.
    """
    ignore = [int(i) for i in ignore]  # '001' -> 1 etc.
    m1 = iter(m1)
    m2 = iter(m2)
    f1 = next(m1, None)
    f2 = next(m2, None)
    diff = []
    while (f1 or f2):
        if (f1.tag == f2.tag):
            if (str(f1) != str(f2) and int(f1.tag) not in ignore):
                diff.append('-< %s' % (str(f1)))
                diff.append('-> %s' % (str(f2)))
            elif (verbose):
                diff.append('== %s' % (str(f1)))
            f1 = next(m1, None)
            f2 = next(m2, None)
        elif (f1.tag < f2.tag):
            if (int(f1.tag) not in ignore):
                diff.append('<< %s' % (str(f1)))
            f1 = next(m1, None)
        elif (f1.tag > f2.tag):
            if (int(f2.tag) not in ignore):
                diff.append('>> %s' % (str(f2)))
            f2 = next(m2, None)
    return('\n'.join(diff))


def main():
    """Command line hander."""
    p = optparse.OptionParser(description='MARC diff',
                              usage='usage: %prog ...')
    p.add_option('--ignore', '-i', action='append', default=[],
                 help="ignore this MARC field (repeatable)")
    p.add_option('--verbose', '-v', action='store_true',
                 help="verbose, show additional informational messages")
    (opt, args) = p.parse_args()

    level = logging.INFO if (opt.verbose) else logging.WARNING
    logging.basicConfig(level=level)
    m1 = read_marc(args[0])
    m2 = read_marc(args[1])
    diff = marc_diff(m1, m2, opt.verbose, opt.ignore)
    print(diff)
    logging.info("Done.")


main()
