from Products.Five.browser import BrowserView
from urlparse import urlparse
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class YoutubeView(BrowserView):
    """Youtube view helper"""

    index = ViewPageTemplateFile('youtube.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.valide = None
        self.url = None
        self.vid

    def update(self):
        if self.url is None:
            self.url = self.context.getRemoteUrl()
        if self.valide is None:
            self.is_valide_url()

    def __call__(self):
        self.update()
        if self.is_valide_url():
            return self.index()

    def is_valide_url(self):
        if self.valide is not None:
            return self.valide
        parsed = urlparse(self.url)
        domain = parsed.netloc == 'www.youtube.com'
        scheme = parsed.scheme in ('http', 'https')
        path = parsed.path == '/watch'
        qs = parsed.query
        params = dict([x.split("=") for x in qs.split("&")])
        self.vid = params.get('v', None)
        vid = bool(self.vid)
        self.valide = domain and scheme and path and vid
