"""Convert BIBFRAME to MARC."""
from rdflib import Graph
from rdflib.namespace import Namespace, RDF
from rdflib_pyld_compat import pyld_json_from_rdflib_graph
from pyld import jsonld
import context_cache.for_pyld
import json
import optparse
import logging


def convert(filename):
    """Convert file into zero or more MARC records."""
    g = Graph()
    g.parse(file=open(filename, 'r'), format='n3')

    # Get JSON-LD object in PyLD form
    jld = pyld_json_from_rdflib_graph(g)
    # print(json.dumps(jld, indent=2, sort_keys=True))

    # Manipulate the JSON in some way (say switch @context
    # to a reference) and output
    # -- no easy way to do this is rdflib
    comp = jsonld.compact(jld, ctx="http://exmaple.org/biblioteko_context.json")
    frame = json.load(open('cache/biblioteko_frame.json', 'r'))
    comp = jsonld.compact(jsonld.frame(comp, frame), ctx="http://exmaple.org/biblioteko_context.json",
                          options={'graph': True})
    logging.info("Framed and compacted JSON-LD:\n" +
                 json.dumps(comp, indent=2, sort_keys=True))

    for obj in comp['@graph']:
        if (obj.get('type') == 'bf:Instance'):
            make_marc(comp, obj)
        else:
            logging.info("Ignoring object %s type %s" %
                         (obj.get('id', 'NO-URI'), obj.get('type', 'NO-TYPE')))


def make_marc(jld, obj):
    """Make one MARC record."""
    inst_id = obj.get('id', 'NO-ID')
    print("# Creating MARC for %s" % (inst_id))
    # <collection xmlns="http://www.loc.gov/MARC21/slim">
    #  <record>
    #    <leader>01050cam a22003011  4500</leader>
    #    <controlfield tag="001">102063</controlfield>
    #    <controlfield tag="008">860506s1957    nyua     b    000 0 eng  </controlfield>
    if ('bib:hasActivity' in obj and
            obj['bib:hasActivity'].get('type') == "bib:PublicationActivity"):
        pub_year = obj['bib:hasActivity'].get('dcterms:date', '')
        pub_loc = ''
        if ('bib:atLocation' in obj['bib:hasActivity']):
            loc = obj['bib:hasActivity']['bib:atLocation'].get('id', '')
            if (loc.startswith('loc:')):
                pub_loc = loc.lstrip('loc:')
        print("008: %s %s" % (pub_year, pub_loc))
    # FIXME - seems that the 'eng' is recorded int the Work but the Work is not linked
    # FIXME - to the Instance!
    #    <datafield tag="245" ind1="0" ind2="0">
    #      <subfield code="a">Clinical cardiopulmonary physiology.</subfield>
    if ('bf:title' in obj and 'rdfs:label' in obj['bf:title']):
        print("245: a %s" % (obj['bf:title']['rdfs:label']))
    #      <subfield code="c">Sponsored by the American College of Chest Physicians.  Editorial board: Burgess L. Gordon, chairman, editor-in-chief, Albert H. Andrews [and others]</subfield>
    if ('bf:responsibilityStatement' in obj):
        print("245: c %s" % (obj['bf:responsibilityStatement']))
    #    </datafield>
    #  </record>
    # </collection>
    print('')


def main():
    """Command line hander."""
    p = optparse.OptionParser(description='BIBFRAME to MARC conversion',
                              usage='usage: %prog workid_bibid_pairs_in.gz] [workid_bibids_out.gz]')
    p.add_option('--src', '-s', action='store', default='testdata/102063.min.ttl',
                 help="input filename (default %default)")
    p.add_option('--verbose', '-v', action='store_true',
                 help="verbose, show additional informational messages")
    (opt, args) = p.parse_args()

    level = logging.INFO if (opt.verbose) else logging.WARNING
    logging.basicConfig(level=level)
    convert(opt.src)
    logging.info("Done.")


main()
