from django.core.cache.backends.memcached import PyLibMCCache
from django.utils.functional import cached_property


class PyLibMCCacheThreadSafe(PyLibMCCache):
    """
    An implementation of a cache binding using thread-safe pylibmc client.
    """

    class ClientWrapper:
        def __init__(self, pool):
            self.pool = pool

        def __getattr__(self, name):
            def method(*args, **kwargs):
                with self.pool.reserve() as client:
                    return getattr(client, name)(*args, **kwargs)

            return method

    @cached_property
    def _cache(self):
        """
        Creates a pool of memcached connections and returns a client wrapper
        to safely execute the operations.
        """
        pool = self._lib.ThreadMappedPool(
            self._class(self.client_servers, **self._options)
        )
        return PyLibMCCacheThreadSafe.ClientWrapper(pool)