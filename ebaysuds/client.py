from ConfigParser import NoOptionError, NoSectionError
from functools import partial

from suds.client import Client
from suds.plugin import DocumentPlugin

from .config import ebaysuds_config
from .transport import WellBehavedHttpTransport


try:
    WSDL_URL = ebaysuds_config.get('soap', 'wsdl_url')
except (NoOptionError, NoSectionError):
    WSDL_URL = "http://developer.ebay.com/webservices/latest/ebaySvc.wsdl"

GATEWAY_URI_QUERYSTRING = "?callname=%(call_name)s&siteid=%(site_id)s&appid=%(app_id)s&version=%(version)s&routing=default"


class EbaySuds(object):
    def __init__(self, wsdl_url=WSDL_URL, sandbox=False, **kwargs):
        self.sudsclient = Client(wsdl_url, cachingpolicy=1, transport=WellBehavedHttpTransport())

        try:
            endpoint = ebaysuds_config.get('soap', 'api_endpoint')
        except (NoOptionError, NoSectionError):
            if sandbox:
                endpoint = 'https://api.sandbox.ebay.com/wsapi'
            else:
                endpoint = 'https://api.ebay.com/wsapi'
        if sandbox:
            key_section = 'sandbox_keys'
        else:
            key_section = 'production_keys'

        self.site_id = kwargs.get('site_id') or ebaysuds_config.get('site', 'site_id')
        self.app_id = kwargs.get('app_id') or ebaysuds_config.get(key_section, 'app_id')

        # do the authentication ritual
        credentials = self.sudsclient.factory.create('RequesterCredentials')
        credentials.eBayAuthToken = kwargs.get('token') or ebaysuds_config.get('auth', 'token')
        credentials.Credentials.AppId = self.app_id
        credentials.Credentials.DevId = kwargs.get('dev_id') or ebaysuds_config.get('keys', 'dev_id')
        credentials.Credentials.AuthCert = kwargs.get('cert_id') or ebaysuds_config.get(key_section, 'cert_id')
        self.sudsclient.set_options(soapheaders=credentials)
        
        # find current API version from the WSDL
        service = self.sudsclient.sd[0].service
        self.version = service.root.getChild('documentation').getChild('Version').text
        
        # add querystring to the service URI specified in WSDL
        # (the service URI can be found in service.ports[0].location but there's no sandbox endpoint in the wsdl)
        self.uri_template = endpoint + GATEWAY_URI_QUERYSTRING

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