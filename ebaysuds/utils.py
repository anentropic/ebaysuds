import os
import shutil
from tempfile import gettempdir as tmp

def clear_cache():
	"""
	Clear the suds object / wsdl cache

    http://pythonaut.blogspot.co.uk/2011/10/how-to-clear-suds-cache.html
	"""
    shutil.rmtree(os.path.join(tmp(), 'suds'), True)