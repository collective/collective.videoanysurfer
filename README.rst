Introduction
============

This addon adds controls over youtube video to display them
while being compliant with anysurfer_ 2.0.

AnySurfer 2.0
=============

French: http://www.anysurfer.org/fr/video-dans-un-lecteur-flash
Nederlands: http://www.anysurfer.org/video-in-een-flashplayer

How to install
==============

This addon can be installed as any other plone addons. Please follow official
documentation_.

This addons depends on:

* collective.js.nomensamediaplayer
* collective.captionmanager

Features
========

* Add play/pause links to control video
* Add transcription and captions support
* Add link options to download MP4 files with subs
* Add components to easy embed youtube video in custom views/viewlet
* Add portlet to display youtube video
* Automatic download of captions from youtube

Players
=======

This addon at the moment supports only nomensa_ jquery media player. By default
this player support TTML captions. You can find a working captions at
https://raw.github.com/nomensa/Accessible-Media-Player/master/example/captions/captions-order-of-content.xml

About Captions Format
=====================

captions format depends on the used player. Nomensa player support only TTML
but the addon collective.captionmanager let you write it in other formats.

SRT (SubRip subtitle)
SBV (YouTube)
Flash DFXP,
SMI or SAMI (Windows Media),
SCC for iOS,
CPT.XML (Flash Captionate XML),
QT (Quicktime)
STL (Spruce Subtitle File).
TTML (<tt ...>) W3C Timed text markup language

How to integrate the player in a template
=========================================

To integrate this player in a custom template you just have to use this snippet::

  <h2><a href="" tal:attributes="href item/link_url" tal:content="item/title">video title</a></h2>
  <div class="nomensa">
    <p>
        <a class="videoanysurfer" tal:attributes="href item/youtube_url" tal:content="item/title">VIDEO TITLE</a>
        <a class="captions" style="display:none;"
           tal:condition="item/captions|nothing" tal:attributes="href item/captions">Captions</a>
    </p>
  </div>

Where item should look like::

  {'youtube_url': 'http://www.youtube.com/watch?v=kXiGXcq4pqY',
  'captions': 'http://localhost:8080/Plone/youtube_link/@@videoanysurfer_captions',
  'link_url': 'http://localhost:8080/Plone/youtube_link',
  'title': 'Order of content by Emily Coward'}

Credits
=======

Companies
---------

|cirb|_ CIRB / CIBG

* `Contact CIRB <mailto:irisline@irisnet.be>`_

Authors

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. Contributors

.. |cirb| image:: http://www.cirb.irisnet.be/logo.jpg
.. _cirb: http://cirb.irisnet.be
.. _anysurfer: http://www.anysurfer.org
.. _nomensa: http://nomensa.com
.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
