import time
import json

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

    def __str__(self):
        return "<%s> (%s)" % (self.url, ", ".join(self.tags))

    def __repr__(self):
        return self.__str__()

    def add_tags(self, *args):
        self.tags |= set(args)

    def update(self):
        self.last_accessed = time.time()

    def parse_urldomain(self):
        from urllib2 import urlparse
        res = urlparse.urlparse(self.url)
        self.url_domain = res.netloc

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
bm = Bookmark("https://en.wikipedia.org/Main_Page")
bm.add_tags("wikipedia", "test", "other tags")
to_json([bm], "test.json")

print from_json("test.json")
