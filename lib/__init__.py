import httplib

def fetch_url(url, id=None):
    if url.lower().startswith("http://"):
        url = url[7:]

    if "/" in url:
        url, path = url.split("/", 1)
    else:
        path = ""

    http = httplib.HTTPConnection(url)
    if id:
        http.request("GET", "/"+path+str(id))
    else:
        http.request("GET", "/"+path)

    response = http.getresponse()
    if response.status != 200:
        raise RuntimeError("'%s' request failed (%d %s)" % (path,
                                                            response.status,
                                                            response.reason))

    return response
