#!/usr/bin/env python
"""Diff two MARC records from given input files."""
import logging
import optparse
from pymarc import parse_xml_to_array
import sys
from mdmux.marcdiff import read_marc, marc_diff


def main():
    """Command line hander."""
    p = optparse.OptionParser(description='MARC diff',
                              usage='usage: %prog [[opts]] file1 file2')
    p.add_option('--ignore', '-i', action='append', default=[],
                 help="ignore this MARC field (repeatable)")
    p.add_option('--verbose', '-v', action='store_true',
                 help="verbose, show additional informational messages")
    (opt, args) = p.parse_args()
    if (len(args) !=2):
        p.error("Must specify two filenames to diff!")

    level = logging.INFO if (opt.verbose) else logging.WARNING
    logging.basicConfig(level=level)
    try:
        m1 = read_marc(args[0])
        m2 = read_marc(args[1])
    except ValueError as e:
        logging.error("Failed to read input: %s" % (str(e)))
        sys.exit(2)
    diff = marc_diff(m1, m2, opt.verbose, opt.ignore)
    print(diff)
    logging.info("Done.")
    # Exit status: 0 if same, 1 if different
    sys.exit(1 if (diff == '') else 0)


main()
