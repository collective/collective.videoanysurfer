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


class IJWPlayerSettings(interface.Interface):
    """Site wide settings for jwplayer"""

    skin = schema.ASCIILine(
        title=u"Skin",
        description=u"A path. For example: /skins/modieus/modieus.zip",
        required=False
    )
        #
#    width = schema.Int(title=u"Width",
#                       required=False)
#
#    height = schema.Int(title=u"Height",
#                        required=False)
#
#    image = schema.URI(title=u"Image of the default player poster",
#                       required=False)
#
#
#class IJWPlayerContextualSettings(interface.Interface):
#    """local settings"""
#
#    autostart = schema.Bool(title=u"Autostart",
#                            required=False)
#    controlbar = schema.Choice(title=u"Control bar",
#                               values=('none', 'bottom'),
#                               required=False)
#
#    width = schema.Int(title=u"Width",
#                       required=False)
#    height = schema.Int(title=u"Height",
#                        required=False)
#
##    file = schema.TextLine(title=u"File path / URL")
#
#    image = schema.URI(title=u"Image of the poster",
#                       required=False)
#
#    duration = schema.TextLine(title=u"Duration",
#                               required=False)
#    start = schema.TextLine(title=u"Start offset",
#                            required=False)
#
#    streamer = schema.Choice(title=u"Streamer",
#                             values=('http', 'rtmp'),
#                             required=False)
#
#    provider = schema.Choice(title=u"Provider",
#                             description=u"pecific media playback API to use \
#                               for playback of this playlist entry.",
#                             values=('http', 'rtmp', 'youtube'),
#                             default='http')
#
#


class Player(object):
    """Register JWplayer into collective.videoanysurfer"""
    interface.implements(vocabulary.IPlayer)

    def __init__(self):
        self.id = "jwplayer"
        self.name = _(u"JWPlayer")
        self.resourceid = RESOURCE_ID
        self.template = ViewPageTemplateFile('jwplayer.pt')
        self.captions_info = CAPTION_REGISTRY["SRT"]


class JWPlayerSettings(BrowserView):
    """A component to get all settings for the contextual player.
    You should override this one in custom project depends on the context"""

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
        if self.settings is None:
            rid = "/++resource++collective.js.jwplayer/player.swf"
            self.settings = {
                "flashplayer": rid,
                "autostart": False,
                "controlbar": "bottom"
            }
            self.extract_settings()

        if self._registry is not None:
            records = self._registry.forInterface(IJWPlayerSettings,
                                                  check=False)
            for name in ('skin',):
                value = getattr(records, name, None)
                if value is not None:
                    self.settings[name] = value

    def __call__(self):
        self.update()
        return "%s" % self.settings

    def jssettings(self):
        """return a javascript string to load settings"""
        self.update()
        return "var %s = %s" % (self.js_var_settings_name,
                                json.dumps(self.settings))

    def extract_settings(self):
        self.settings['file'] = self.context.getRemoteUrl()
