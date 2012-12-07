========
ebaysuds
========

Why
===

Most of the Python libs for using eBay APIs I found are based on the *Plain XML* API. Which basically means the author of the lib has to handcode request-builder functions for every method they intend to support.

eBay have over *a hundred and fifty* methods accessible via their APIs, each with some required and dozens of optional args. This basically means all the Python eBay libs are very incomplete and probably out of date too, because it's such a pain to maintain them.

SOAP
----
eBay provide a *SOAP API* too. The SOAP API is basically just the XML API with some additional verbose XML wrapping around it. But one advantage of the SOAP API is it has a *WSDL* …another XML file (`5.3MB currently <http://developer.ebay.com/webservices/latest/ebaySvc.wsdl>`_) that describes all the request methods and args and their types and responses.

Python already has an excellent SOAP lib in the form of `Suds <https://fedorahosted.org/suds/>`_. So it seems like a better approach would be to use eBay's SOAP API via Suds…

Dirty…
------
…eBay's implementation of SOAP/WSDL seems to be a bit idiosyncratic (possibly… *wrong*) - at least it's not as smooth to call methods via Suds as it could be. 

Clean Again…
------------
So I made this thin wrapper around Suds, so that you can easily use *all* of the eBay API methods, in up-to-the-minute form, from Python.

See GitHub for usage and docs.