# Copyright (C) 2001 - 2024 David Fillmore
#
# This file is part of ififf.
#
# ififf is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ififf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from xml.dom.minidom import parseString


def getbibliographic(iFiction):
    dom = parseString(iFiction)
    try:
        story = dom.getElementsByTagName('story')[0]  # assumes only one story element
        biblio = story.getElementsByTagName('bibliographic')[0]
    except:
        return None
    return biblio


def getTitle(iFiction):
    try:
        biblio = getbibliographic(iFiction)
        title = biblio.getElementsByTagName('title')[0]
        return title.childNodes[0].wholeText
    except:
        return None


def getHeadline(iFiction):
    try:
        biblio = getbibliographic(iFiction)
        headline = biblio.getElementsByTagName('headline')[0]
        return headline.childNodes[0].wholeText
    except:
        return None


def getAuthor(iFiction):
    try:
        biblio = getbibliographic(iFiction)
        author = biblio.getElementsByTagName('author')[0]
        return author.childNodes[0].wholeText
    except:
        return None


def getDescription(iFiction):
    try:
        biblio = getbibliographic(iFiction)
        desc = biblio.getElementsByTagName('description')[0]
        fulldesc = []

        return ''.join([ ('\n\n' if a.nodeType == 1 and a.localName == 'br' else ' '.join(a.wholeText.split())) for a in desc.childNodes
                       ]
                      )
    except:
        return None


def getZcode(iFiction):
    try:
        dom = parseString(iFiction)
        story = dom.getElementsByTagName('story')[0]  # assumes only one story element
        zcode = story.getElementsByTagName('zcode')[0]
        return zcode
    except:
        return None


def getCoverPicture(iFiction):
    zcode = getZcode(iFiction)
    try:
        coverpicture = zcode.getElementsByTagName('coverpicture')
        return int(coverpicture[0].childNodes[0].wholeText)
    except:
        return None
