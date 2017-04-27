#!/usr/bin/env python
"""Convert BIBFRAME to MARC."""
from rdflib import Graph
from rdflib.namespace import Namespace, RDF
from rdflib_pyld_compat import pyld_json_from_rdflib_graph
from pyld import jsonld
from pymarc import Record, Field, XMLWriter
from io import BytesIO
import context_cache.for_pyld
import json
import optparse
import logging
import re


def convert(filename, dump_json=False):
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
    comp = jsonld.compact(jsonld.frame(comp, frame),
                          ctx="http://exmaple.org/biblioteko_context.json",
                          options={'graph': True})
    if (dump_json):
        logging.info("Framed and compacted JSON-LD:\n" +
                     json.dumps(comp, indent=2, sort_keys=True))
    memory = BytesIO()
    writer = XMLWriter(memory)
    for obj in comp['@graph']:
        if (obj.get('type') == 'bf:Instance'):
            writer.write(make_marc(comp, obj))
        else:
            logging.info("Ignoring object %s type %s" %
                         (obj.get('id', 'NO-URI'), obj.get('type', 'NO-TYPE')))
    writer.close(close_fh=False)  # Important!
    xml = memory.getvalue().decode(encoding='UTF-8')
    # Dumb semi pretty print
    xml = re.sub(r'(</\w+>)', r'\1\n', xml)
    xml = re.sub(r'(\?>)', r'\1\n', xml)
    xml = re.sub(r'(<record>)', r'\n\1\n', xml)
    return(xml)


def obj_has_type(obj, rdf_type=None):
    """True is obj includes the given type."""
    types = obj.get('type')
    if (not isinstance(types, list)):
        types = [types]
    for t in types:
        if (rdf_type == t):
            return True
    return False


def find_obj_by_id(jld, obj_id, rdf_type=None):
    """Find top-level object with id obj_id in jld."""
    for obj in jld['@graph']:
        logging.debug("find_obj_by_id: looking at %s" % (obj.get('id')))
        if (obj.get('id') == obj_id):
            if (obj_has_type(obj, rdf_type)):
                return(obj)
            raise Exception("Found object id=%s but has type %s not %s" %
                            (obj_id, obj.get('type'), rdf_type))
    raise Exception("Failed to find object %s" % (obj_id))


def make_marc(jld, obj):
    """Make one MARC record."""
    inst_id = obj.get('id', 'NO-ID')
    logging.info("Creating MARC for %s" % (inst_id))
    record = Record()
    # Find associated work
    if ('bf:instanceOf' in obj and
        'id' in obj['bf:instanceOf']):
        work = find_obj_by_id(jld, obj['bf:instanceOf']['id'], 'bf:Work')
    else:
        raise Exception("No bf:instanceOf so can't get work!")
    # <collection xmlns="http://www.loc.gov/MARC21/slim">
    #  <record>
    #    <leader>01050cam a22003011  4500</leader>
    #    <controlfield tag="001">102063</controlfield>
    #    <controlfield tag="008">860506s1957    nyua     b    000 0 eng  </controlfield>
    if ('bib:hasActivity' in obj and
            obj['bib:hasActivity'].get('type') == "bib:PublicationActivity"):
        # https://www.loc.gov/marc/bibliographic/bd008.html
        pub_year = obj['bib:hasActivity'].get('dcterms:date', '')
        pub_loc = ''
        pub_lang = ''
        if ('bib:atLocation' in obj['bib:hasActivity']):
            loc = obj['bib:hasActivity']['bib:atLocation'].get('id', '')
            if (loc.startswith('loc:')):
                pub_loc = loc.lstrip('loc:')
        if ('dcterms:language' in work):
            lang = work['dcterms:language'].get('id', '')
        if (lang.startswith('lang:')):
            pub_lang = lang.lstrip('lang:')
        f008 = "%6s%1s%4s%4s%3s%17s%3s%1s%1s" % ('', '', pub_year, '', pub_loc, '', pub_lang, '', '')
        record.add_field(Field(tag = '008', data = f008))
    # FIXME - seems that the 'eng' is recorded int the Work but the Work is not linked
    # FIXME - to the Instance!
    #    <datafield tag="245" ind1="0" ind2="0">
    #      <subfield code="a">Clinical cardiopulmonary physiology.</subfield>
    f245 = []
    if ('bf:title' in obj and 'rdfs:label' in obj['bf:title']):
        f245.append('a')
        f245.append(obj['bf:title']['rdfs:label'])
    #      <subfield code="c">Sponsored by the American College of Chest Physicians.  Editorial board: Burgess L. Gordon, chairman, editor-in-chief, Albert H. Andrews [and others]</subfield>
    if ('bf:responsibilityStatement' in obj):
        f245.append('c')
        f245.append(obj['bf:responsibilityStatement'])
    if (len(f245) > 0):
        record.add_field(Field(tag = '245', indicators = [0, 0],
                               subfields = f245))
    #    </datafield>
    #  </record>
    # </collection>
    return(record)


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

    level = logging.DEBUG if opt.debug else (logging.INFO
        if opt.verbose else logging.WARNING)
    logging.basicConfig(level=level)

    xml = convert(opt.src, opt.json)
    print(xml)
    logging.info("Done.")


main()
