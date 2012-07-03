from zope import component
from zope import interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


class IPlayer(interface.Interface):
    """A player"""

    def resourceid(self):
        """Return the resource ID"""

    def name(self):
        """return the player name"""


class PlayerVocabulary(object):
    interface.implements(IVocabularyFactory)
    query_type = ""

    def __call__(self, context):
        players = component.getUtilitiesFor(IPlayer)
        terms = []

        for name, instance in players:
            terms.append(SimpleTerm(name, name, instance.name))

        return SimpleVocabulary(terms)

PlayerVocabularyFactory = PlayerVocabulary()