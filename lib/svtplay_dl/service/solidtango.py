# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
from __future__ import absolute_import
import re

from svtplay_dl.service import Service
from svtplay_dl.fetcher.hls import hlsparse
from svtplay_dl.error import ServiceError


class Solidtango(Service):
    supported_domains_re = [r'^([^.]+\.)*solidtango.com']
    supported_domains = ['mm-resource-service.herokuapp.com']

    def get(self):
        data = self.get_urldata()

        if self.exclude(self.options):
            yield ServiceError("Excluding video")
            return
        match = re.search('src="(http://mm-resource-service.herokuapp.com[^"]*)"', data)
        if match:
            data = self.http.request("get", match.group(1)).text
            match = re.search('src="(https://[^"]+solidtango[^"]+)" ', data)
            if match:
                data = self.http.request("get", match.group(1)).text
        match = re.search(r'<title>(http[^<]+)</title>', data)
        if match:
            data = self.http.request("get", match.group(1)).text

        match = re.search('is_livestream: true', data)
        if match:
            self.options.live = True
        match = re.search('html5_source: "([^"]+)"', data)
        if match:
            streams = hlsparse(self.options, self.http.request("get", match.group(1)), match.group(1))
            for n in list(streams.keys()):
                yield streams[n]
        else:
            yield ServiceError("Can't find video info. if there is a video on the page. its a bug.")
            return