# mdmux

*Health warning* - Hacked up nastiness messing about with conversion of BIBFRAME/bibliotek-o back to MARC. This may or may not turn into anything useful, it certainly isn't even nearly there yet!

Philosophy is to take BIBFRAME or bibliotek-o RDF (in some format the `rdflib` can read), convert to JSON-LD in memory, use JSON-LD framing to restructure as a set of `bf:Work`, `bf:Instance` and `bf:Item` objects, and then build MARC record from these using `pymarc`. I wonder whether it will work?
