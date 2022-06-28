# Source code from (https://github.com/Taapat/enigma2-plugin-youtube/blob/master/src/compat.py)
from sys import version_info

PY3 = version_info[0] == 3


# Disable certificate verification on python 2.7.9
if version_info >= (2, 7, 9):
	import ssl
	ssl._create_default_https_context = ssl._create_unverified_context


if version_info[0] == 2:
	# Python 2
	compat_str = unicode

	from urllib import urlencode as compat_urlencode
	from urllib import quote as compat_quote
	from urllib2 import urlopen as compat_urlopen
	from urllib2 import Request as compat_Request
	from urllib2 import HTTPError as compat_HTTPError
	from urllib2 import URLError as compat_URLError
	from urlparse import urljoin as compat_urljoin
	from urlparse import urlparse as compat_urlparse
	from urlparse import urlunparse as compat_urlunparse
	from httplib import HTTPException as compat_HTTPException
else:
	# Python 3
	compat_str = str

	from urllib.parse import urlencode as compat_urlencode
	from urllib.parse import quote as compat_quote
	from urllib.request import urlopen as compat_urlopen
	from urllib.request import Request as compat_Request
	from urllib.error import HTTPError as compat_HTTPError
	from urllib.error import URLError as compat_URLError
	from urllib.parse import urljoin as compat_urljoin
	from urllib.parse import urlparse as compat_urlparse
	from urllib.parse import parse_qs as compat_parse_qs
	from urllib.parse import urlunparse as compat_urlunparse
	from http.client import HTTPException as compat_HTTPException
