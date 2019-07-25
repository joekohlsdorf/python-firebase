import requests
import os  # for os.path.dirname
import json  # for dumps
from six.moves.urllib.parse import urljoin, urlparse

DEFAULT_TIMEOUT = 5  # timeout in seconds


class Firebase(object):
    ROOT_URL = ''  # no trailing slash
    REQUEST_ARGS = {}

    def __init__(self, root_url, auth_token=None, request_args={}):
        self.ROOT_URL = root_url.rstrip('/')
        self.REQUEST_ARGS = request_args
        self.auth_token = auth_token

    def __str__(self):
        return self.ROOT_URL

    # these methods are intended to mimic Firebase API calls.

    def child(self, path):
        root_url = '%s/' % self.ROOT_URL
        url = urljoin(root_url, path.lstrip('/'))
        return Firebase(url)

    def parent(self):
        url = os.path.dirname(self.ROOT_URL)
        # if url is the root of your Firebase, return None
        up = urlparse(url)
        if up.path == '':
            return None  # maybe throw exception here?
        return Firebase(url)

    def name(self):
        return os.path.basename(self.ROOT_URL)

    def set(self, value):
        return self.put(value)

    def push(self, data):
        return self.post(data)

    def update(self, data):
        return self.patch(data)

    def remove(self):
        return self.delete()

    # these mirrors REST API functionality

    def put(self, data):
        return self.__request('put', data=data)

    def patch(self, data):
        return self.__request('patch', data=data)

    def get(self):
        return self.__request('get')

    def post(self, data):
        """
        POST differs from PUT in that it is equivalent to doing a 'push()' in
        Firebase where a new child location with unique name is generated and
        returned
        """
        return self.__request('post', data=data)

    def delete(self):
        return self.__request('delete')

    def __request(self, method, **kwargs):
        kwargs.setdefault('timeout', DEFAULT_TIMEOUT)
        kwargs.update(self.REQUEST_ARGS)

        # Firebase API does not accept form-encoded PUT/POST
        # data. It needs to be JSON encoded.
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])

        params = {}
        if self.auth_token:
            if 'params' in kwargs:
                params = kwargs['params']
                del kwargs['params']
            params.update({'auth': self.auth_token})

        r = requests.request(method, self.url, params=params, **kwargs)
        r.raise_for_status()  # throw exception if error
        return r.json()

    @property
    def url(self):
        # we append .json to end of ROOT_URL for REST API.
        return '%s.json' % self.ROOT_URL
