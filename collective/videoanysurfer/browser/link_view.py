from zope import component
from zope import interface
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.configviews.browser.configurable_view import ConfigurableBaseView
from collective.videoanysurfer.video import IVideoAnySurfer, IVideoExtraData
from urlparse import urlparse
from urllib import urlopen
from Products.Five.browser import BrowserView
from plone.autoform.form import AutoExtensibleForm
from z3c.form import form
from AccessControl.security import checkPermission
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
        self.extra = None

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
            self.portal_state = component.getMultiAdapter((self.context,
                                                          self.request),
                                                name=u'plone_portal_state')
        if self.extra is None:
            self.extra = component.queryAdapter(self.context, IVideoExtraData)
            self.extra.update()

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
        captions = self.extra.captions
        if not captions:
            return

        return "%s/@@videoanysurfer_captions" % self.context.absolute_url()

    def is_youtube(self):
        return self.youtube

    def language(self):
        return self.portal_state.language()

    def canedit(self):
        return checkPermission("cmf.ModifyPortalContent", self.context)

    def context_url(self):
        return self.context.absolute_url()


class VideoCaptions(BrowserView):

    def __call__(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        self.request.response.setHeader('Content-Type', 'text/xml')
        extra = component.queryAdapter(self.context, IVideoExtraData)
        if extra:
            extra.update()
            return extra.captions


class VideoExtraDataEditForm(AutoExtensibleForm, form.EditForm):
    schema = IVideoExtraData

    def getContent(self):
        extra = component.queryAdapter(self.context, IVideoExtraData)
        if extra:
            extra.update()
            return {'captions': extra.captions,
                    'transcription': extra.transcription}

    def applyChanges(self, data):
        extra = component.queryAdapter(self.context, IVideoExtraData)
        if extra:
            extra.update()
            extra.captions = data.get('captions', '')
            extra.transcription = data.get('transcription', '')
            self.request.response.redirect(self.context.absolute_url())
            return True

from plone.app.z3cform.layout import wrap_form

VideoExtraDataEditFormView = wrap_form(VideoExtraDataEditForm)
