"""Convert BIBFRAME to MARC."""
from rdflib import Graph
from rdflib.namespace import Namespace, RDF
from rdflib_pyld_compat import pyld_json_from_rdflib_graph
from pyld import jsonld
from pymarc import Record, Field, XMLWriter
from io import BytesIO
import context_cache.for_pyld
import json
import re
import sys
import logging


class Converter(object):
    """BIBFRAME to MARC converter class."""

    def __init__(self, dump_json=False):
        """Initialize Converter, set flags."""
        self.jsonld = None
        # From options
        self.dump_json = dump_json

    def convert(self, filename):
        """Convert file into zero or more MARC records."""
        g = Graph()
        with open(filename, 'r') as fh:
            g.parse(file=fh, format='n3')

        # Get JSON-LD object in PyLD form
        jld = pyld_json_from_rdflib_graph(g)
        # print(json.dumps(jld, indent=2, sort_keys=True))

        # Manipulate the JSON in some way (say switch @context
        # to a reference) and output
        # -- no easy way to do this is rdflib
        comp = jsonld.compact(jld, ctx="http://exmaple.org/biblioteko_context.json")
        with open('cache/biblioteko_frame.json', 'r') as ffh:
            frame = json.load(ffh)
        comp = jsonld.compact(jsonld.frame(comp, frame),
                              ctx="http://exmaple.org/biblioteko_context.json",
                              options={'graph': True})
        if (self.dump_json):
            sys.stderr.write("Framed and compacted JSON-LD:\n" +
                             json.dumps(comp, indent=2, sort_keys=True) + '\n')
        self.jsonld = comp

        memory = BytesIO()
        writer = XMLWriter(memory)
        for obj in self.jsonld['@graph']:
            if (obj.get('type') == 'bf:Instance'):
                writer.write(self.make_marc(obj))
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

    def obj_has_type(self, obj, rdf_type=None):
        """True is obj includes the given type."""
        types = obj.get('type')
        if (not isinstance(types, list)):
            types = [types]
        for t in types:
            if (rdf_type == t):
                return True
        return False

    def find_obj_by_id(self, obj_id, rdf_type=None):
        """Find top-level object with id obj_id."""
        for obj in self.jsonld['@graph']:
            logging.debug("find_obj_by_id: looking at %s" % (obj.get('id')))
            if (obj.get('id') == obj_id):
                if (self.obj_has_type(obj, rdf_type)):
                    return(obj)
                raise Exception("Found object id=%s but has type %s not %s" %
                                (obj_id, obj.get('type'), rdf_type))
        raise Exception("Failed to find object %s" % (obj_id))

    def make_marc(self, obj):
        """Make one MARC record."""
        inst_id = obj.get('id', 'NO-ID')
        logging.info("Creating MARC for %s" % (inst_id))
        record = Record()
        # Find associated work
        if ('bf:instanceOf' in obj and 'id' in obj['bf:instanceOf']):
            work = self.find_obj_by_id(obj['bf:instanceOf']['id'], 'bf:Work')
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
            record.add_field(Field(tag='008', data=f008))
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
            record.add_field(Field(tag='245', indicators=[0, 0],
                                   subfields=f245))
        #    </datafield>
        #  </record>
        # </collection>
        return(record)
