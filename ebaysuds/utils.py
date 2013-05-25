import os
import shutil
from tempfile import gettempdir as tmp

from suds.sudsobject import asdict


def clear_cache():
    """
    Clear the suds object / wsdl cache

    http://pythonaut.blogspot.co.uk/2011/10/how-to-clear-suds-cache.html
    """
    shutil.rmtree(os.path.join(tmp(), 'suds'), True)


def recursive_asdict(d):
    """
    Recursively convert Suds object into dict.

    http://stackoverflow.com/a/15678861/202168
    """
    out = {}
    for k, v in asdict(d).iteritems():
        if hasattr(v, '__keylist__'):
            out[k] = recursive_asdict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(recursive_asdict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out