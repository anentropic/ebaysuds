ebaysuds
========

```
from ebaysuds.service import EbaySuds
client = EbaySuds()
client.GetItem(ItemID="321021906488")
```

Most of the Python libs for using eBay APIs I found are based on the _Plain XML_ API. Which basically means the author of the lib has to handcode request-builder functions for every method they intend to support.

eBay have over _a hundred and fifty_ methods accessible via their APIs, each with some required and dozens of optional args. This basically means all the Python eBay libs are very incomplete and probably out of date too, because it's such a pain to maintain them.

SOAP
----
eBay provide a _SOAP API_ too. The SOAP API is basically just the XML API with some additional verbose XML wrapping around it. But one advantage of the SOAP API is it has a _WSDL_… another XML file ([5.3MB currently](http://developer.ebay.com/webservices/latest/ebaySvc.wsdl)) that describes all the request methods and args and their types and responses.

Python already has an excellent SOAP lib in the form of [Suds](https://fedorahosted.org/suds/). So it seems like a better approach would be to use eBay's SOAP API via Suds...

Dirty…
------
…eBay's implementation of SOAP/WSDL seems to be a bit idiosyncratic (possibly… _wrong_) or at least it's not as smooth to call methods via Suds as it could be. 

Clean Again…
------------
So I made this thin wrapper around Suds, so that you can easily use *all* of the eBay API methods, in up-to-the-minute form, from Python.

You can see the code itself is fairly trivial, but 