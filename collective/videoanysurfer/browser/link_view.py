#python
from urllib import urlopen
from captionstransformer.registry import REGISTRY as CAPTION_REGISTRY
from captionstransformer import youtube
from StringIO import StringIO

#zope
from zope import component
from z3c.form import form, button
from AccessControl.security import checkPermission
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from z3c.form.i18n import MessageFactory as _z

#plone
from plone.autoform.form import AutoExtensibleForm
from plone.registry.interfaces import IRegistry
from plone.app.z3cform.layout import wrap_form

#collective
from collective.videoanysurfer.video import IVideoExtraData
from collective.videoanysurfer.browser.vocabulary import IPlayer
from collective.videoanysurfer.i18n import _

CAPTIONS_URL = "%s/@@videoanysurfer_captions?captions_format=%s"


class LinkView(BrowserView):
    """Link View helper"""
    index = ViewPageTemplateFile('link_view.pt')

    def __init__(self, context, request):
        super(LinkView, self).__init__(context, request)
        self.youtube = None
        self.vid = None
        self.portal_state = None
        self.context_state = None
        self.extra = None
        self.player = None

    def update(self):
        if self.youtube is None:
            self.youtube = youtube.get_video_id(self.context.getRemoteUrl())

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

        if not self.extra.captions:
            return

        format = self.player.captions_info["id"]
        context_url = self.context.absolute_url()

        return CAPTIONS_URL % (context_url, format)

    def language(self):
        return self.context.Language()

    def canedit(self):
        return checkPermission("cmf.ModifyPortalContent", self.context)

    def context_url(self):
        return self.context.absolute_url()

    def embed_player(self):
        if self.player is not None:
            return self.player.template(self)
        return self.context.translate(_(u"No configured player."))


class VideoCaptions(BrowserView):

    def update_request(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')

    def get_format(self):
        return self.request.get('captions_format', 'TTML')

    def __call__(self):
        self.update_request()
        return self.get_captions()

    def get_captions(self):
        format = self.get_format()
        extra = component.queryAdapter(self.context, IVideoExtraData)

        if extra:
            extra.update()
            format_info = CAPTION_REGISTRY[format]
            self.request.response.setHeader('Content-Type',
                                format_info["mimetype"])

            if extra.captions_format and extra.captions_format["id"] != format:
                return self.transform(extra, format)

            return extra.captions

    def transform(self, extra, target):
        captions = extra.captions
        eid = extra.captions_format["id"]

        if eid == target:
            return captions

        sio = StringIO(extra.captions)
        reader = extra.captions_format["reader"](sio)
        captions = reader.read()
        if captions:
            writer = CAPTION_REGISTRY[target]["writer"](StringIO())
            writer.set_captions(captions)
            return writer.captions_to_text()


class VideoExtraDataEditForm(AutoExtensibleForm, form.EditForm):
    schema = IVideoExtraData

    def getContent(self):
        extra = component.queryAdapter(self.context, IVideoExtraData)
        if extra:
            extra.update()
            #FIXME: captions format is not saved
            if extra.captions_format:
                captions_format = extra.captions_format['id']
            else:
                captions_format = "TTML"
            return {'captions': extra.captions,
                    'captions_format': captions_format,
                    'transcription': extra.transcription,
                    'download_url': extra.download_url}

    def getExtra(self):
        extra = component.queryAdapter(self.context, IVideoExtraData)

        if extra:
            extra.update()

        return extra

    #really strange: when adding an action, the apply one is removed.
    # lets add it back
    @button.buttonAndHandler(_z('Apply'), name='apply')
    def handleApply(self, action):
        #those weird decorator change the signature ... lets copy/paste code
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

    def applyChanges(self, data):
        extra = self.getExtra()
        if extra:
            extra.transcription = data.get('transcription', '')
            extra.download_url = data.get('download_url', '')
            extra.captions_format = data.get('captions_format', '')

            data_captions = data.get('captions', '')
            if not data_captions and extra.captions:
                extra.captions = ''
            elif data_captions:
                extra.captions = data_captions

            self.request.response.redirect(self.context.absolute_url())

            return True

    @button.buttonAndHandler(_('Update from youtube'), name='update')
    def handleUpdate(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyUpdate(data)
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

    def applyUpdate(self, data):
        extra = self.getExtra()

        if extra:
            url = self.context.getRemoteUrl()
            language = self.context.Language()
            reader = youtube.get_reader(url, language)

            if reader:
                reader.read()
                extra.captions = reader.rawcontent
                extra.captions_format = 'transcript'  # force format

            self.request.response.redirect(self.context.absolute_url())

            return True

        return False

    @button.buttonAndHandler(_('Delete'), name='delete')
    def handleDelete(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyDelete()
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

    def applyDelete(self):
        extra = self.getExtra()

        if extra:
            extra.captions = u''
            extra.transcription = u''
            extra.download_url = ''
            extra.captions_format = ''
            self.request.response.redirect(self.context.absolute_url())
            return True

        return False


VideoExtraDataEditFormView = wrap_form(VideoExtraDataEditForm)
