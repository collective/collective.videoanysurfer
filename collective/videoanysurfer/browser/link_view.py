from zope.component import getMultiAdapter
from zope import interface
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.configviews.browser.configurable_view import ConfigurableBaseView
from collective.videoanysurfer.video import IVideoAnySurfer
from urlparse import urlparse
from urllib import urlopen
from Products.Five.browser import BrowserView
YOUTUBE_TRANS = "http://video.google.com/timedtext?lang=%(lang)s&v=%(vid)s"


class LinkView(ConfigurableBaseView):
    """Link View helper"""
    index = ViewPageTemplateFile('link_view.pt')
    settings_schema = IVideoAnySurfer

    def __init__(self, context, request):
        super(LinkView, self).__init__(context, request)
        self.youtube = None
        self.vid = None
        self.portal_state = None

    def update(self):
        if self.youtube is None:
            parsed = urlparse(self.video_url())
            domain = parsed.netloc == 'www.youtube.com'
            scheme = parsed.scheme in ('http', 'https')
            path = parsed.path == '/watch'
            qs = parsed.query
            params = dict([x.split("=") for x in qs.split("&")])
            self.vid = params.get('v', None)
            vid = bool(self.vid)
            self.youtube = domain and scheme and path and vid

        if self.portal_state is None:
            self.portal_state = getMultiAdapter((self.context,
                                                 self.request),
                                                name=u'plone_portal_state')

    def __call__(self):
        self.update()
        return self.index()

    def download_uri(self):
        return self.settings.download_uri

    def transcription_uri(self):
        return self.settings.transcription_uri

    def transcription(self):
        return self.settings.transcription

    def video_url(self):
        return self.context.getRemoteUrl()

    def video_title(self):
        return self.context.Title()

    def captions(self):
        nav_url = self.portal_state.navigation_root_url()
        if self.is_youtube():
            return "%s/@@videoanysurfer_transcription" % nav_url

    def is_youtube(self):
        return self.youtube

    def language(self):
        return self.portal_state.language()


class VideoTranscription(BrowserView):

    def __call__(self):
        vid = self.request.get('vid', None)
        lang = self.request.get('lang', 'en')
        query = {'lang': lang, 'vid': vid}
        import pdb;pdb.set_trace()
        return urlopen(YOUTUBE_TRANS % query).read()
