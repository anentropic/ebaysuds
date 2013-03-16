import logging
from ConfigParser import NoOptionError, NoSectionError
from functools import partial

from suds.client import Client
from suds.plugin import DocumentPlugin

from .config import production_config, sandbox_config, CONFIG_PATH
from .transport import WellBehavedHttpTransport


logging.basicConfig()
log = logging.getLogger(__name__)

# I wish I didn't have to do this,, see:
# http://developer.ebay.com/DevZone/merchandising/docs/Concepts/SiteIDToGlobalID.html
SITE_ID_TO_GLOBAL_ID = {
    0: 'EBAY-US',
    2: 'EBAY-ENCA',
    3: 'EBAY-GB',
    15: 'EBAY-AU',
    16: 'EBAY-AT',
    23: 'EBAY-FRBE',
    71: 'EBAY-FR',
    77: 'EBAY-DE',
    100: 'EBAY-MOTOR',
    101: 'EBAY-IT',
    123: 'EBAY-NLBE',
    146: 'EBAY-NL',
    186: 'EBAY-ES',
    193: 'EBAY-CH',
    201: 'EBAY-HK',
    203: 'EBAY-IN',
    205: 'EBAY-IE',
    207: 'EBAY-MY',
    210: 'EBAY-FRCA',
    211: 'EBAY-PH',
    212: 'EBAY-PL',
    216: 'EBAY-SG',
}

def make_querystring(**kwargs):
    return "?%s" % "&".join(["%s=%s" % (k,v) for k,v in kwargs.items()])

class APIBase(object):
    """
    AbstractBaseClass: don't instantiate this, use a concrete sub-class
    """
    WSDL = None

    PRODUCTION_ENDPOINT = None
    SANDBOX_ENDPOINT = None

    def _get_conf_prefix(self):
        # assume the class name ends in 'API'
        return self.__class__.__name__[:-3].lower()

    def __init__(self, sandbox=False, **kwargs):
        # eBay API methods are all CamelCase so it should be safe to set any
        # lowercase (or all-caps) attributes we want...

        self.CONF_PREFIX = self._get_conf_prefix()
        self.sandbox = sandbox
        if sandbox:
            self.config = sandbox_config
        else:
            self.config = production_config

        try:
            self.WSDL = self.config.get('soap', '%s_wsdl' % self.CONF_PREFIX)
        except (NoOptionError, NoSectionError):
            if self.WSDL is None:
                raise NotImplementedError(
                    'You must give a value for WSDL on a sub-class, or define'\
                    ' <api name>_wsdl in the conf file'
                )

        try:
            self._endpoint = self.config.get('soap', '%s_api' % self.CONF_PREFIX)
        except (NoOptionError, NoSectionError):
            if sandbox:
                if self.SANDBOX_ENDPOINT is None:
                    raise NotImplementedError(
                        'You must give a value for SANDBOX_ENDPOINT on a sub-'\
                        'class, or define <api name>_api in the conf file'
                    )
                self._endpoint = self.SANDBOX_ENDPOINT
            else:
                if self.SANDBOX_ENDPOINT is None:
                    raise NotImplementedError(
                        'You must give a value for PRODUCTION_ENDPOINT on a '\
                        'sub-class, or define <api name>_api in the conf file'
                    )
                self._endpoint = self.PRODUCTION_ENDPOINT

        self.sudsclient = Client(self.WSDL, cachingpolicy=1, transport=WellBehavedHttpTransport())

        log.info('CONFIG_PATH: %s', CONFIG_PATH)
        self.site_id = kwargs.get('site_id') or self.config.get('site', 'site_id')
        self.app_id = kwargs.get('app_id') or self.config.get('keys', 'app_id')

        # find current API version from the WSDL
        service = self.sudsclient.sd[0].service
        self.version = service.root.getChild('documentation').getChild('Version').text

        # later we add a querystring to the service URI specified in WSDL
        # (the service URI can be found in service.ports[0].location but there's no sandbox
        # wsdl, so we can't endpoint in the wsdl)  

    def __getattr__(self, name):
        """
        A wrapper over the the suds service method invocation makes interface
        nicer and gives the opportunity to do the extra stuff required by
        ebay's weird implementations of SOAP
        """
        return getattr(self.sudsclient.service, name)


class TradingAPI(APIBase):
    WSDL = 'http://developer.ebay.com/webservices/latest/ebaySvc.wsdl'

    PRODUCTION_ENDPOINT = 'https://api.ebay.com/wsapi'
    SANDBOX_ENDPOINT = 'https://api.sandbox.ebay.com/wsapi'

    def __init__(self, wsdl_url=None, sandbox=False, **kwargs):
        # allow to pass in a wsdl url, bypassing conf file etc
        if wsdl_url is not None:
            self.WSDL = wsdl_url
        super(TradingAPI, self).__init__(sandbox=sandbox, **kwargs)

        # do the authentication ritual
        credentials = self.sudsclient.factory.create('RequesterCredentials')
        credentials.Credentials.AppId = self.app_id
        credentials.Credentials.DevId = kwargs.get('dev_id') or self.config.get('keys', 'dev_id')
        credentials.Credentials.AuthCert = kwargs.get('cert_id') or self.config.get('keys', 'cert_id')
        credentials.eBayAuthToken = kwargs.get('token') or self.config.get('auth', 'token')
        self.sudsclient.set_options(soapheaders=credentials)
    
    def __getattr__(self, name):
        method = super(TradingAPI, self).__getattr__(name=name)

        # for some reason ebay require some fields from the SOAP request to be repeated
        # as querystring args appended to the service url
        qs_args = {
            'callname': name,
            'siteid': self.site_id,
            'appid': self.app_id,
            'version': self.version,
            'routing': 'default',
        }
        method.method.location = self._endpoint + make_querystring(**qs_args)

        # ...and the method call itself always has to specify an API version (again)
        return partial(method, Version=self.version)


class ShoppingAPI(APIBase):
    WSDL = 'http://developer.ebay.com/webservices/latest/ShoppingService.wsdl'

    PRODUCTION_ENDPOINT = 'http://open.api.ebay.com/shopping'
    SANDBOX_ENDPOINT = 'http://open.api.sandbox.ebay.com/shopping'

    def __getattr__(self, name):
        method = super(ShoppingAPI, self).__getattr__(name=name)

        # for some reason ebay require some fields from the SOAP request to be repeated
        # as querystring args appended to the service url
        qs_args = {
            'callname': name,
            'siteid': self.site_id,
            'appid': self.app_id,
            'version': self.version,
            'responseencoding': 'SOAP',
        }
        method.method.location = self._endpoint + make_querystring(**qs_args)
        return method


class FindingAPI(APIBase):
    WSDL = 'http://developer.ebay.com/webservices/Finding/latest/FindingService.wsdl'

    PRODUCTION_ENDPOINT = 'http://svcs.ebay.com/services/search/FindingService/v1'
    SANDBOX_ENDPOINT = 'http://svcs.sandbox.ebay.com/services/search/FindingService/v1'

    def __getattr__(self, name):
        method = super(FindingAPI, self).__getattr__(name=name)

        http_headers = {
            'X-EBAY-SOA-OPERATION-NAME': name,
            'X-EBAY-SOA-SERVICE-NAME': 'FindingService',# this one is just genius
            'X-EBAY-SOA-SERVICE-VERSION': self.version,
            'X-EBAY-SOA-GLOBAL-ID': SITE_ID_TO_GLOBAL_ID[int(self.site_id,10)],
            'X-EBAY-SOA-SECURITY-APPNAME': self.app_id,
            'X-EBAY-SOA-REQUEST-DATA-FORMAT': 'SOAP',
            'X-EBAY-SOA-MESSAGE-PROTOCOL': 'SOAP12',
        }
        self.sudsclient.set_options(headers=http_headers)
        return method
