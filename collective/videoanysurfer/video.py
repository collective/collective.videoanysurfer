from zope import interface
from zope import schema
from zope import i18nmessageid
_ = i18nmessageid.MessageFactory('collective.videoanysurfer')


download_url_title = _(u"Download url")
download_url_desc = _(u"""You may provide a download URL in MP4 format with
subtitles in it to let people being able to watch the video. """)

transcription_title = _(u"Transcription")
transcription_desc = _(u"""You may provide the audio transcription of the
current video here.""")
transcription_uri_title = _(u"Transcription URL")
transcription_uri_desc = _(u"Please push the XML transcription file to use")


class IVideoAnySurfer(interface.Interface):
    """Any surfer 2.0 metadata"""

    download_uri = schema.URI(title=download_url_title,
                              description=download_url_desc)

    transcription_uri = schema.URI(title=transcription_uri_title,
                                   description=transcription_uri_desc)

    transcription = schema.Text(title=transcription_title,
                                description=transcription_desc)
