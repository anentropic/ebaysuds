# ebaysuds

Most of the Python libs for using eBay APIs I found are based on the _Plain XML_ API. Which basically means the author of the lib has to handcode request-builder functions for every method they intend to support.

eBay have over _a hundred and fifty_ methods accessible via their APIs, each with some required and dozens of optional args. This basically means all the Python eBay libs are very incomplete and probably out of date too, because it's such a pain to maintain them.

### SOAP
eBay provide a _SOAP API_ too. The SOAP API is basically just the XML API with some additional verbose XML wrapping around it. But one advantage of the SOAP API is it has a _WSDL_… another XML file ([5.3MB currently](http://developer.ebay.com/webservices/latest/ebaySvc.wsdl)) that describes all the request methods and args and their types and responses.

Python already has an excellent SOAP lib in the form of [Suds](https://fedorahosted.org/suds/). So it seems like a better approach would be to use eBay's SOAP API via Suds...

### Dirty…
…eBay's implementation of SOAP/WSDL seems to be a bit idiosyncratic (possibly… _wrong_) - at least it's not as smooth to call methods via Suds as it could be. 

### Clean Again…
So I made this thin wrapper around Suds, so that you can easily use *all* of the eBay API methods, in up-to-the-minute form, from Python.

```python
from ebaysuds.service import EbaySuds
client = EbaySuds()
client.GetItem(ItemID="321021906488")
```

You can see the source code itself is fairly trivial, but it took me a couple of days wrestling with eBay's extensive-but-crap docs to get to this point.

## Getting started

1. First you need to get yourself some developer keys [from eBay here](https://developer.ebay.com/DevZone/account/)
2. You need to make a `ebaysuds.conf` file in the root of your project (or `export EBAYSUDS_CONFIG_PATH=<path to conf>` in your shell)
3. Easiest way is to copy `ebaysuds.conf-example` from this repo and fill in the blanks. `site_id` is the [code of the eBay site](http://developer.ebay.com/DevZone/XML/docs/WebHelp/FieldDifferences-Site_IDs.html) your profile is on.

That's it. Well, you need to [read the docs](http://developer.ebay.com/DevZone/XML/docs/WebHelp/wwhelp/wwhimpl/js/html/wwhelp.htm?href=Overview-.html) from eBay to see how to make the calls you want.

### A spot of pruning

So yeah, you probably noticed it's really slow to initialise that client the first time?

Behind the scenes we're _downloading a 5.3MB XML file and parsing it into Python objects_.

Hmm, SOAP doesn't seem so hot now? Well it's mitigated partly by telling Suds to cache the WSDL (and parsed Python objects).

But eBay also recognise the problem and provide:

> [WSDL Pruner Tool](http://developer.ebay.com/DevZone/codebase/wsdlpruner/pruner.zip): Lets you prune a bulky WSDL down to the operations that you want to use

Go ahead, download it. Yes it's a lovely Java jar file.

It comes with some rudimentary docs explaining how to launch the thing, which is a simple GUI app allowing you to save a new WSDL with just the methods you want to use.

A single-method WSDL (the ones I tried) still comes out about 1.6MB(!) but a lot of that is documentation text and XML overhead, so probably a lot less Python objects than if you have all 160 methods.

You need to host the WSDL on a web server 