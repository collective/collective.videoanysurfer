from urlparse import urlparse

from AccessControl.security import checkPermission
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from zope import component
from z3c.form import form
from plone.autoform.form import AutoExtensibleForm
from plone.registry.interfaces import IRegistry
from collective.videoanysurfer.video import IVideoExtraData
from collective.videoanysurfer.browser.vocabulary import IPlayer
from collective.videoanysurfer.i18n import _

YOUTUBE_TRANS = "http://video.google.com/timedtext?lang=%(lang)s&v=%(vid)s"


class LinkView(BrowserView):
    """Link View helper"""
    index = ViewPageTemplateFile('link_view.pt')

    def __init__(self, context, request):
        super(LinkView, self).__init__(context, request)
        self.youtube = None
        self.vid = None
        self.portal_state = None
        self.extra = None
        self.player = None

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

        if self.player is None:
            registry = component.getUtility(IRegistry)
            player = registry['collective.videoanysurfer.player']
            if player is not None:
                self.player = component.queryUtility(IPlayer,
                                                     name=player)

    def __call__(self):
        self.update()
        return self.index()

    def download_url(self):
        return self.extra.download_url

    def transcription(self):
        return self.extra.transcription

    def video_url(self):
        return self.context.getRemoteUrl()

    def video_title(self):
        return self.context.Title()

    def captions(self):
        captions = self.extra.captions
        if not captions:
            return

        return "%s/@@videoanysurfer_captions" % self.context.absolute_url()

    def language(self):
        return self.portal_state.language()

    def canedit(self):
        return checkPermission("cmf.ModifyPortalContent", self.context)

    def context_url(self):
        return self.context.absolute_url()

    def embed_player(self):
        if self.player is not None:
            return self.player.template(self)
        return self.context.translate(_(u"No configured player."))


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
            extra.download_url = data.get('download_url', '')
            self.request.response.redirect(self.context.absolute_url())
            return True

from plone.app.z3cform.layout import wrap_form

VideoExtraDataEditFormView = wrap_form(VideoExtraDataEditForm)
