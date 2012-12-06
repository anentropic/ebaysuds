"""
From:
https://gist.github.com/3721801

Author:
https://github.com/rbarrois

Not strictly necessary but makes it a lot easier to debug the requests
and responses if you can use a proxy to inspect them
(eg http://charlesproxy.com)
"""
from suds.transport.http import HttpTransport as SudsHttpTransport 


class WellBehavedHttpTransport(SudsHttpTransport): 
    """HttpTransport which properly obeys the ``*_proxy`` environment variables.""" 
 
    def u2handlers(self): 
        """Return a list of specific handlers to add. 
 
        The urllib2 logic regarding ``build_opener(*handlers)`` is: 
 
        - It has a list of default handlers to use 
 
        - If a subclass or an instance of one of those default handlers is given 
            in ``*handlers``, it overrides the default one. 
 
        Suds uses a custom {'protocol': 'proxy'} mapping in self.proxy, and adds 
        a ProxyHandler(self.proxy) to that list of handlers. 
        This overrides the default behaviour of urllib2, which would otherwise 
        use the system configuration (environment variables on Linux, System 
        Configuration on Mac OS, ...) to determine which proxies to use for 
        the current protocol, and when not to use a proxy (no_proxy). 
 
        Thus, passing an empty list will use the default ProxyHandler which 
        behaves correctly. 
        """ 
        return []
