# Django pylibmc thread-unsafe
The goal of this repository is to simulate a race condition in Django's implementation for accessing Memcached using the pylibmc library in a multi-threaded environment.

## Context
The Django cache implementation for the pylibmc library (`django.core.cache.backends.memcached.PyLibMCCache`) uses the default client, without pooling connections. This library is not thread-safe by default. Although Django stores the cache connections using a thread-safe implementation, there are scenarios where a race condition can occur. This repository demonstrates the following scenario:

- A Django application using the `django.middleware.cache.FetchFromCacheMiddleware` and `django.middleware.cache.UpdateCacheMiddleware` middlewares.
    - That way we force cache utilization between the requests.
- A route that receives a key to be stored in cache, which is requested by multiple users.
    - If the key doesn't exist in cache, it is stored using the key as the value.
    - If the key exists in cache, the system checks if the key used is the same as the returned value.
        - If the key and value are not the same, a key mismatch occurs.

## Steps to reproduce the problem
1. Start the application and Memcached containers:
    - `$ docker-compose up`
2. Run the Locust test:
    - `$ make test`

It'll simulates multiple users requesting the same key from the cache to trigger the race condition. When the problema happens, the test will be finished with a return like this: 
```
$ make test
[2024-06-05 18:57:11,599] bf64d050534c/INFO/locust.main: Run time limit set to 60 seconds
[2024-06-05 18:57:11,600] bf64d050534c/INFO/locust.main: Starting Locust 2.28.0
Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                         0     0(0.00%) |      0       0       0      0 |    0.00        0.00

[2024-06-05 18:57:11,601] bf64d050534c/INFO/locust.runners: Ramping to 10 users at a rate of 1.00 per second
{"error": "*** Keys mismatch detected - key: test-1, value: <JsonResponse status_code=200, \"application/json\"> ***"}
Reached target status code
make: *** [test] Error 1
```
In this case we requested the cache value for the key `test-1` and received a cached Django view response.

## How to fix it? 
There are more than one way to address this issue, here we've some examples: 
- Don't use threads
    - If you are using uWSGI you can just disable the threads config and use only processes instead
- Don't use the pylibmc implementation
    - There are other alternatives, but the pylibmc seems to be the one with better performance 
- Use the `ThreadMappedPool` client as suggested from the pylibmc lib
    - There's an implementation example [here](/cache/cache.py) in this repo, you can use it and set the `PyLibMCCacheThreadSafe` in your `CACHES` config
    - There's also [this gist](https://gist.github.com/mrts/334682) with another implementation example
- Use the [django-pylibmc-threadsafe](https://github.com/mireq/django-pylibmc-threadsafe)
