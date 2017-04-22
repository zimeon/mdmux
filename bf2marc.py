"""Convert BIBFRAME to MARC."""
from rdflib import Graph
from rdflib.namespace import Namespace, RDF
from rdflib_pyld_compat import pyld_json_from_rdflib_graph
from pyld import jsonld
import context_cache.for_pyld
import json

g = Graph()
g.parse(file=open('testdata/102063.min.ttl', 'r'), format='n3')

## Get JSON-LD object in PyLD form
jld = pyld_json_from_rdflib_graph(g)
#print(json.dumps(jld, indent=2, sort_keys=True))


# Manipulate the JSON in some way (say switch @context
# to a reference) and output
# -- no easy way to do this is rdflib
comp = jsonld.compact(jld, ctx="http://exmaple.org/biblioteko_context.json")
frame = json.load(open('cache/biblioteko_frame.json', 'r'))
comp = jsonld.compact(jsonld.frame(comp, frame), ctx="http://exmaple.org/biblioteko_context.json",
                      options={'graph': True})
#print(json.dumps(comp, indent=2, sort_keys=True))

for obj in comp['@graph']:
    if (obj.get('type') == 'bf:Instance'):
        print(obj)
    else:
        print("Ignoring object %s type %s" %(obj.get('id', 'NO-URI'), obj.get('type', 'NO-TYPE')))
