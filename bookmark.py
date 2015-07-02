import sys
import time
import json
from urllib2 import urlparse
import httplib

class Bookmark(object):
    def __init__(self, url, tags=set()):
        self.url = url
        self.parse_urldomain()

        self.created = time.time()
        self.last_accessed = self.created
        self.tags = set()
        self.add_tags(*tags)
        self.filetype = None
        self._cached = False
        self.is_alive = False
        self.check_alive()

    def __str__(self):
        return "<%s> (%s)" % (self.url, ", ".join(self.tags))

    def __repr__(self):
        return self.__str__()

    def __follow_redirect(self, newurl):

        _total_tries = 2
        while _total_tries > 0:

            sch, dom, path = self.parse_urldomain(newurl)
            if sch == "http":
                conn = httplib.HTTPConnection(dom)
            else:
                conn = httplib.HTTPSConnection(dom)

            conn.request("GET", path)
            resp = conn.getresponse()
            _total_tries -= 1
            #print "New status: %d" % resp.status
            if resp.status in (301, 302):
                #print >>sys.stderr, "Number of redirects: %d" % (10 - _total_tries)
                headers = dict(resp.getheaders())
                newnewurl = resp.getheader("location")
                if newurl == newnewurl:
                    return None, resp
                #print "Redirecting: %s -> %s" % (newurl, newnewurl)
                newurl = newnewurl
                continue

            break

        return newurl, resp

    def check_alive(self):
        if self._scheme == "http":
            conn = httplib.HTTPConnection(self.url_domain)
        else:
            conn = httplib.HTTPSConnection(self.url_domain)
        conn.request("GET", self._fullpath)
        resp = conn.getresponse()
        if resp.status in (301, 302):
            init_stat = resp.status
            redirect = resp.getheader("location")
            #print "Redirecting: %s -> %s" % (self.url, redirect)
            url, resp = self.__follow_redirect(redirect)
            if init_stat == 301 and url is not None:
                self.url = url
                self.update()

        if resp.status != 200:
            #print "Not alive: %d %s" % (resp.status, resp.reason)
            self.is_alive = False
        else:
            self.is_alive = True
        return resp.status

    def add_tags(self, *args):
        self.tags |= set(args)

    def update(self):
        self.check_alive()
        self.last_accessed = time.time()

    def parse_urldomain(self, url=None):
        res = urlparse.urlparse(self.url)
        if url is None:
            self._scheme = res.scheme
            self.url_domain = res.netloc
            self._path = res.path
            self._remainder = (res.path, res.params, res.query, res.fragment)
            self._fullpath = "".join((res.path, res.params, res.query, res.fragment))
        return res.scheme, res.netloc, "".join((res.path, res.params, res.query, res.fragment))

    def to_html(self, sort_by=None):
        pass

EXPORT_FIELDS = ["created", "last_accessed", "filetype", "_cached"]
def to_json(bookmarks, fname):
    json_dict = {}
    for bm in bookmarks:
        json_dict[bm.url] = dict(((field, getattr(bm, field)) for field in EXPORT_FIELDS))
        json_dict[bm.url]["tags"] = list(bm.tags)
    with open(fname, "w") as fout:
        json.dump(json_dict, fout)
    return json_dict

def from_json(fname):
    with open(fname) as fin:
        json_dict = json.load(fin)
    bookmarks = []
    for url, b in json_dict.iteritems():
        bm = Bookmark(url)
        bm.add_tags(*b["tags"])
        for key in EXPORT_FIELDS:
            setattr(bm, key, b[key])
        bookmarks.append(bm)
    return bookmarks

# Test code
bm = Bookmark("https://en.wikipedia.org/wiki/Main_Page")
bm.add_tags("wikipedia", "test", "other tags")
to_json([bm], "test.json")
print from_json("test.json")
