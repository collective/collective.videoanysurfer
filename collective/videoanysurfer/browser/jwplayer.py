#python
from captionstransformer.registry import REGISTRY as CAPTION_REGISTRY
try:
    import simplejson as json
except ImportError:
    import json

#zope
from zope import component
from zope import interface
from zope import schema

#cmf
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

#plone
from plone.registry.interfaces import IRegistry

from collective.videoanysurfer.i18n import _
from collective.videoanysurfer.browser import vocabulary

HAS_Player = True
try:
    from collective.js.jwplayer.config import RESOURCE_ID
except ImportError:
    HAS_Player = False
    RESOURCE_ID = ""


class IJWPlayerSiteSettings(interface.Interface):
    """Site wie settings for jwplayer"""

    skin = schema.ASCIILine(title=u"Skin",
                  description=u"A path. For example: \
                    /skins/modieus/modieus.zip",
                  required=False)

    width = schema.Int(title=u"Width",
                       required=False)

    height = schema.Int(title=u"Height",
                        required=False)

    image = schema.URI(title=u"Image of the default player poster",
                       required=False)


class IJWPlayerContextualSettings(interface.Interface):
    """local settings"""

    autostart = schema.Bool(title=u"Autostart",
                            required=False)
    controlbar = schema.Choice(title=u"Control bar",
                               values=('none', 'bottom'),
                               required=False)

    width = schema.Int(title=u"Width",
                       required=False)
    height = schema.Int(title=u"Height",
                        required=False)

#    file = schema.TextLine(title=u"File path / URL")

    image = schema.URI(title=u"Image of the poster",
                       required=False)

    duration = schema.TextLine(title=u"Duration",
                               required=False)
    start = schema.TextLine(title=u"Start offset",
                            required=False)

    streamer = schema.Choice(title=u"Streamer",
                             values=('http', 'rtmp'),
                             required=False)

    provider = schema.Choice(title=u"Provider",
                             description=u"pecific media playback API to use \
                               for playback of this playlist entry.",
                             values=('http', 'rtmp', 'youtube'),
                             default='http')


class IJWPlayerSettings(IJWPlayerSiteSettings, IJWPlayerContextualSettings):
    """jwplayer settings"""


class Player(object):
    """Register JWplayer into collective.videoanysurfer"""
    interface.implements(vocabulary.IPlayer)

    def __init__(self):
        self.id = "jwplayer"
        self.name = _(u"JWPlayer")
        self.resourceid = RESOURCE_ID
        self.template = ViewPageTemplateFile('jwplayer.pt')
        self.captions_info = CAPTION_REGISTRY["SRT"]

    def get_settings(self, videosettings):
        return {
         "flashplayer": "/++resource++collective.js.jwplayer/player.swf",
         "autostart": False,
         "controlbar": "bottom",
         "file": videosettings['url'],
         "width": videosettings['width']
         }


class JWPlayerSettings(BrowserView):
    """A component to get all settings for the contextual player"""

    interface.implements(IJWPlayerSettings)
    js_var_settings_name = "jwplayersettings"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._registry = None
        self._lregistry = None
        self.settings = None

    def update(self):
        if self._registry is None:
            self._registry = component.queryUtility(IRegistry)
        if self._lregistry is None:
            self._lregistry = component.queryAdapter(self.context, IRegistry)
        if self.settings is None:
            self.settings = {}

            records = self._registry.forInterface(IJWPlayerSiteSettings)
            for name in ('skin', 'width', 'height', 'image'):
                value = getattr(records, name, None)
                if value:
                    self.settings[name] = value

        if self._context_registry:
            records = self._lregistry.forInterface(IJWPlayerContextualSettings)
            for name in ('skin', 'width', 'height', 'image', 'duration',
                         'start', 'streamer', 'provider',
                         'autostart', 'controlbar'):
                value = getattr(records, name, None)
                if value:
                    self.settings[name] = value

    def __call__(self):
        self.update()
        return self.index()

    def jssettings(self):
        """return a javascript string to load settings"""
        return "var %s = %s" % (self.js_var_settings_name,
                                json.dumps(self.settings))
