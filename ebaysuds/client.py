from ConfigParser import NoOptionError
from functools import partial

from suds.client import Client
from suds.plugin import DocumentPlugin

from .config import ebaysuds_config
from .transport import WellBehavedHttpTransport


try:
    WSDL_URL = ebaysuds_config.has_option('wsdl', 'url')
except NoOptionError:
    WSDL_URL = "http://developer.ebay.com/webservices/latest/ebaySvc.wsdl"
GATEWAY_URI_QUERYSTRING = "?callname=%(call_name)s&siteid=%(site_id)s&appid=%(app_id)s&version=%(version)s&routing=default"


class EbaySuds(object):
    def __init__(self, wsdl_url=WSDL_URL):
        self.sudsclient = Client(wsdl_url, cachingpolicy=1, transport=WellBehavedHttpTransport())
        self.site_id = ebaysuds_config.get('site', 'site_id')
        self.app_id = ebaysuds_config.get('keys', 'app_id')

        # do the authentication ritual
        credentials = self.sudsclient.factory.create('RequesterCredentials')
        credentials.eBayAuthToken = ebaysuds_config.get('auth', 'token')
        credentials.Credentials.AppId = self.app_id
        credentials.Credentials.DevId = ebaysuds_config.get('keys', 'dev_id')
        credentials.Credentials.AuthCert = ebaysuds_config.get('keys', 'cert_id')
        self.sudsclient.set_options(soapheaders=credentials)
        
        # find current API version from the WSDL
        service = self.sudsclient.sd[0].service
        self.version = service.root.getChild('documentation').getChild('Version').text
        
        # add querystring to the service URI specified in WSDL
        self.uri_template = service.ports[0].location + GATEWAY_URI_QUERYSTRING

    def __getattr__(self, name):
        """
        A wrapper over the the suds service method invocation to do the extra stuff
        required by ebay's weird implementation of SOAP
        """
        method = getattr(self.sudsclient.service, name)

        # for some reason ebay require some fields from the SOAP request to be repeated
        # as querystring args appended to the service url
        method.method.location = self.uri_template % {
            'call_name': name,
            'site_id': self.site_id,
            'app_id': self.app_id,
            'version': self.version,
        }
        
        # ...and the method call itself always has to specify an API version (again)
        return partial(method, Version=self.version)