#!/usr/bin/env python
"""Command line tool to convert BIBFRAME to MARC."""
import optparse
import logging
from mdmux.bf2marc import Converter


def main():
    """Command line hander."""
    p = optparse.OptionParser(description='BIBFRAME to MARC conversion',
                              usage='usage: %prog workid_bibid_pairs_in.gz] [workid_bibids_out.gz]')
    p.add_option('--src', '-s', action='store', default='testdata/102063.min.ttl',
                 help="input filename (default %default)")
    p.add_option('--json', '-j', action='store_true',
                 help="dump JSON-LD intermediate")
    p.add_option('--verbose', '-v', action='store_true',
                 help="verbose, show additional informational messages")
    p.add_option('--debug', action='store_true',
                 help="very verbose, show debugging information")
    (opt, args) = p.parse_args()

    level = logging.DEBUG if opt.debug else \
        (logging.INFO if opt.verbose else logging.WARNING)
    logging.basicConfig(level=level)

    c = Converter(dump_json=opt.json)
    xml = c.convert(opt.src)
    print(xml)
    logging.info("Done.")


main()
