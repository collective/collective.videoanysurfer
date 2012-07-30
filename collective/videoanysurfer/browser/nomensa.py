#python
from captionstransformer.registry import REGISTRY as CAPTION_REGISTRY

#zope
from zope import interface
from zope import i18nmessageid

#CMF
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
_ = i18nmessageid.MessageFactory('collective.videoanysurfer')

#plone

#collective
from collective.videoanysurfer.browser import vocabulary
HAS_PLAYER = True
try:
    from collective.js.nomensa.config import RESOURCE_ID
except ImportError:
    HAS_PLAYER = False
    RESOURCE_ID = ""


class Player(object):
    """Register JWplayer into collective.videoanysurfer"""
    interface.implements(vocabulary.IPlayer)

    def __init__(self):
        self.id = "nomensa"
        self.name = _(u"Nomensa Player")
        self.resourceid = RESOURCE_ID
        self.template = ViewPageTemplateFile('nomensa.pt')
        self.captions_info = CAPTION_REGISTRY["TTML"]
