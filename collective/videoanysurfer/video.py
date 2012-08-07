#python
from captionstransformer.registry import REGISTRY as CAPTION_REGISTRY

#zope
from zope import interface
from zope import schema
from zope import i18nmessageid
from zope.annotation.interfaces import IAnnotations
import persistent

from collective.captionmanager.vocabulary import format_vocabulary

_ = i18nmessageid.MessageFactory('collective.videoanysurfer')

download_url_title = _(u"Download url")
download_url_desc = _(u"You may provide a download URL in MP4 format with\
subtitles in it to let people being able to watch the video. ")

transcription_title = _(u"Transcription")
transcription_desc = _(u"You may provide the audio transcription of the\
current video here. It is pure text")
transcription_uri_title = _(u"Transcription URL")
transcription_uri_desc = _(u"Please push the XML transcription file to use")
transcription_raw_title = _(u"Transcription Raw text")
transcription_raw_desc = _(u"This text will be displayed next to the video")


class IVideoAnySurfer(interface.Interface):
    """Any surfer 2.0 metadata"""

#
#    transcription_uri = schema.URI(title=transcription_uri_title,
#                                   description=transcription_uri_desc,
#                                   required=False)
#
#    transcription_xml = schema.Text(title=transcription_title,
#                                description=transcription_desc,
#                                required=False)
#
#    transcription_raw = schema.Text(title=transcription_raw_title,
#                                    description=transcription_raw_desc,
#                                    required=False)

captions_title = _(u"Captions")
captions_desc = _(u"XML content to display during video playing")
format_title = _(u"Captions Format")


class IVideoExtraData(interface.Interface):
    """Adding data to improve video accessibility"""

    captions = schema.Text(title=captions_title,
                           description=captions_desc,
                           required=False)

    captions_format = schema.Choice(title=format_title,
                                    vocabulary=format_vocabulary)

    transcription = schema.Text(title=transcription_title,
                                description=transcription_desc,
                                required=False)

    download_url = schema.URI(title=download_url_title,
                              description=download_url_desc,
                              required=False)

VIDEO_EXTRADATA_KEY = "collective.videoanysurfer.videoextradata"


class VideoExtraData(object):
    """implement video extra data using annotation"""
    interface.implements(IVideoExtraData)

    def __init__(self, context):
        self.context = context
        self.storage = None
        self._annotations = None

    def update(self):
        if self.storage is None:
            self._annotations = IAnnotations(self.context)
            if self._annotations.get(VIDEO_EXTRADATA_KEY,
                                     None) is None:
                self.storage = persistent.dict.PersistentDict()
                self._annotations[VIDEO_EXTRADATA_KEY] = self.storage
            else:
                self.storage = self._annotations[VIDEO_EXTRADATA_KEY]

    def get_captions(self):
        return self.storage.get('captions', '')

    def set_captions(self, value):
        self.storage['captions'] = value

    def del_captions(self):
        del self.storage['captions']

    captions = property(get_captions, set_captions, del_captions)

    def get_transcription(self):
        return self.storage.get('transcription', '')

    def set_transcription(self, value):
        self.storage['transcription'] = value

    def del_transcription(self):
        del self.storage['transcription']

    transcription = property(get_transcription, set_transcription,
                             del_transcription)

    def get_download_url(self):
        return self.storage.get('download_url', '')

    def set_download_url(self, value):
        self.storage['download_url'] = value

    def del_download_url(self):
        del self.storage['download_url']

    download_url = property(get_download_url, set_download_url,
                            del_download_url)

    def set_captions_format(self, value):
        self.storage['captions_format'] = value

    def get_captions_format(self):
        captions_format = self.storage.get('captions_format', None)
        if captions_format:
            return CAPTION_REGISTRY[captions_format]

    def del_captions_format(self):
        del self.storage['captions_format']

    captions_format = property(get_captions_format, set_captions_format,
                               del_captions_format)


