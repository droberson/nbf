#!/usr/bin/env python3

# TODO config file for setting up filters
# TODO save filters to disk before exiting
# TODO normal bloom filters
# TODO change server banner
# TODO instruction using apache/nginx as reverse proxy
# TODO logging
# TODO daemonize, pid file, watchdog script
# TODO specify listen address/port
# TODO IPv6
# TODO docstrings
# TODO script to build bloom filters + example uses
# TODO HUP reloads config / saves configs

from dmfrbloom.timefilter import TimeFilter

from twisted.web import server, resource
from twisted.web.resource import Resource
from twisted.internet import reactor

TIMEFILTER = TimeFilter(10000, 0.001, 60*60)

FILTERS = [
    # [name of filter, filter object, write permissions?],
    ["tftest", TIMEFILTER, True],
]


class NBFRoot(Resource):
    @staticmethod
    def render_GET(request):
        print(request.method, request.uri, request.path, request.args,
              request.requestHeaders, request.getClientAddress())
        return b"<html><body><a href=\"https://github.com/droberson/nbf\">NBF</a></body></html"


class NBFTimeFilter(Resource):
    @staticmethod
    def render_GET(request):
        status = 404
        for bfilter in FILTERS:
            if request.args[b"filter"][0].decode("utf-8") == bfilter[0]:
                result = bfilter[1].lookup(request.args[b"element"][0])
                status = 200 if result else 204
            break
        request.setResponseCode(status)
        return b""

    @staticmethod
    def render_POST(request):
        status = 404
        for bfilter in FILTERS:
            if request.args[b"filter"][0].decode("utf-8") == bfilter[0]:
                if bfilter[1]: # Check for write permission
                    status = 200
                    bfilter[1].add(request.args[b"element"][0])
                    break
                status = 403
                break
        request.setResponseCode(status)
        return b""


def main():
    nbf = Resource()
    nbf.putChild(b"", NBFRoot())
    nbf.putChild(b"timefilter", NBFTimeFilter())
    reactor.listenTCP(9999, server.Site(nbf), interface="", backlog=50)
    #reactor.listenTCP(9998, server.Site(nbf), interface="::")
    reactor.run()


if __name__ == "__main__":
    main()
