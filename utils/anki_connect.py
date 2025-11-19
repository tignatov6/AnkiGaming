import requests
import json

class AnkiConnect():
    def __init__(self, anki_address='http://localhost:8765'):
        self.anki_address = anki_address
        pass

    def version(self):
        """
        :return: :class:`str` object
        :rtype: API version number
        
        """
        return self.send_request("version")

    def requestPermission(self, origin, allowed):
        """
        :return: :class:`str` object
        :rtype: permission

        :return: :class:`bool` object
        :rtype: requireApikey

        :return: :class:`int` object
        :rtype: version
        """

        result = self.send_request("requestPermission",origin=origin, allowed=allowed)
        return result['permission'], result['requireApikey'], result['version']
        
    def getProfiles(self):
        """
        :return: :class:`list[str]` object
        :rtype: profiles list
        """
        result = self.send_request('getProfiles')
        return result

    def getActiveProfile(self):
        """
        :return: :class:`str` object
        :rtype: profile name
        """
        result = self.send_request("getActiveProfile")
        return result

    def loadProfile(self, name):
        """
        Загружает профиль с определённым именем.

        :return: :class:`bool` object
        :rtype: success
        """

        result = self.send_request("loadProfile",name=name)
        return result

    def sync(self):
        """
        Синхронизировать коллекции(колоды и карточки)
        """
        self.send_request("sync")

    def multi(self, actions):
        """
        Выполняет несколько действий в одном запросе (batch processing).
        Это значительно повышает производительность при выполнении множества операций.
        
        :param actions: Список действий для выполнения. Каждое действие — это словарь 
                        с ключами 'action', 'params' (опционально) и 'version' (опционально)
        :type actions: list[dict]
        :return: Список результатов для каждого действия в том же порядке
        :rtype: list[Any]
        """
        result = self.send_request("multi", actions=actions)
        return result

    def getNumCardsReviewedToday(self):
        """
        :return: :class:`int` object
        :rtype: number of cards
        """
        result = self.send_request("getNumCardsReviewedToday")
        return result

    def getNumCardsReviewedByDay(self):
        """
        :return: :class:`list[list[str,int]]` object
        :rtype: list of lists with date and number of reviewed cards
        """
        result = self.send_request("getNumCardsReviewedByDay")
        return result

    def getCollectionStatsHTML(self, wholeCollection=True):
        """
        :return: :class:`str` object
        :rtype: HTML stats of Collection ¯\_(ツ)_/¯
        """
        result = self.send_request("getCollectionStatsHTML")
        return result

    def deckNames(self):
        """
        :return: :class:`list[str]` object
        :rtype: list of all deck names
        """
        result = self.send_request("deckNames")
        return result

    def deckNamesAndIds(self):
        """
        :return: :class:`dict[deck_name]: id` object
        :rtype: dict of all deck names as keys and ids as values
        """
        result = self.send_request("deckNamesAndIds")
        return result

    def getDecks(self, cards):
        """
        Принимает список карт, а выдаёт ⬇️

        :return: :class:`dict[deck]: list[card]` object
        :rtype: dict of all deck names as keys and cards as values
        """
        result = self.send_request("getDecks",cards=cards)
        return result

    def createDeck(self, deck):
        pass

    def changeDeck(self, cards, deck):
        pass

    def deleteDecks(self, decks, cardsToo=False):
        pass

    def getDeckConfig(self, deck):
        pass

    def saveDeckConfig(self, config):
        pass

    def setDeckConfigId(self, decks, configId):
        pass

    def cloneDeckConfigId(self, name, cloneFrom='1'):
        pass

    def removeDeckConfigId(self, configId):
        pass

    def getDeckStats(self, decks):
        pass

    def storeMediaFile(self, filename, data=None, path=None, url=None, skipHash=None, deleteExisting=True):
        pass

    def retrieveMediaFile(self, filename):
        pass

    def getMediaFilesNames(self, pattern='*'):
        pass

    def deleteMediaFile(self, filename):
        pass

    def getMediaDirPath(self):
        pass

    def addNote(self, note):
        pass

    def canAddNote(self, note):
        pass

    def canAddNoteWithErrorDetail(self, note):
        pass

    def updateNoteFields(self, note):
        pass

    def updateNote(self, note):
        pass

    def updateNoteModel(self, note):
        pass

    def updateNoteTags(self, note, tags):
        pass

    def getNoteTags(self, note):
        pass

    def addTags(self, notes, tags, add=True):
        pass

    def removeTags(self, notes, tags):
        pass

    def getTags(self):
        pass

    def clearUnusedTags(self):
        pass

    def replaceTags(self, notes, tag_to_replace, replace_with_tag):
        pass

    def replaceTagsInAllNotes(self, tag_to_replace, replace_with_tag):
        pass

    def setEaseFactors(self, cards, easeFactors):
        pass

    def setSpecificValueOfCard(self, card, keys,newValues, warning_check=False):
        pass

    def getEaseFactors(self, cards):
        pass

    def suspend(self, cards, suspend=True):
        pass

    def unsuspend(self, cards):
        pass

    def suspended(self, card):
        pass

    def areSuspended(self, cards):
        pass

    def areDue(self, cards):
        pass

    def getIntervals(self, cards, complete=False):
        pass

    def modelNames(self):
        pass

    def createModel(self, modelName, inOrderFields, cardTemplates, css = None, isCloze = False):
        pass

    def modelNamesAndIds(self):
        pass

    def findModelsById(self, modelIds):
        pass

    def findModelsByName(self, modelNames):
        pass

    def modelNameFromId(self, modelId):
        pass

    def modelFieldNames(self, modelName):
        pass

    def modelFieldDescriptions(self, modelName):
        pass

    def modelFieldFonts(self, modelName):
        pass

    def modelFieldsOnTemplates(self, modelName):
        pass

    def modelTemplates(self, modelName):
        pass

    def modelStyling(self, modelName):
        pass

    def updateModelTemplates(self, model):
        pass

    def updateModelStyling(self, model):
        pass

    def findAndReplaceInModels(self, modelName, findText, replaceText, front=True, back=True, css=True):
        pass

    def modelTemplateRename(self, modelName, oldTemplateName, newTemplateName):
        pass

    def modelTemplateReposition(self, modelName, templateName, index):
        pass

    def modelTemplateAdd(self, modelName, template):
        pass

    def modelTemplateRemove(self, modelName, templateName):
        pass

    def modelFieldRename(self, modelName, oldFieldName, newFieldName):
        pass

    def modelFieldReposition(self, modelName, fieldName, index):
        pass

    def modelFieldAdd(self, modelName, fieldName, index=None):
        pass

    def modelFieldRemove(self, modelName, fieldName):
        pass

    def modelFieldSetFont(self, modelName, fieldName, font):
        pass

    def modelFieldSetFontSize(self, modelName, fieldName, fontSize):
        pass

    def modelFieldSetDescription(self, modelName, fieldName, description):
        pass

    def deckNameFromId(self, deckId):
        pass

    def findNotes(self, query=None):
        pass

    def findCards(self, query=None):
        pass

    def cardsInfo(self, cards):
        pass

    def cardsModTime(self, cards):
        pass

    def forgetCards(self, cards):
        pass

    def relearnCards(self, cards):
        pass

    def answerCards(self, answers):
        pass

    def cardReviews(self, deck, startID):
        pass

    def getReviewsOfCards(self, cards):
        pass

    def setDueDate(self, cards, days):
        pass

    def reloadCollection(self):
        pass

    def getLatestReviewID(self, deck):
        pass

    def insertReviews(self, reviews):
        pass

    def notesInfo(self, notes=None, query=None):
        pass

    def notesModTime(self, notes):
        pass

    def deleteNotes(self, notes):
        pass

    def removeEmptyNotes(self):
        pass

    def cardsToNotes(self, cards):
        pass

    def guiBrowse(self, query=None, reorderCards=None):
        pass

    def guiEditNote(self, note):
        pass

    def guiSelectNote(self, note):
        pass

    def guiSelectCard(self, card):
        pass

    def guiSelectedNotes(self):
        pass

    def guiAddCards(self, note=None):
        pass

    def guiReviewActive(self):
        pass

    def guiCurrentCard(self):
        pass

    def guiStartCardTimer(self):
        pass

    def guiShowQuestion(self):
        pass

    def guiShowAnswer(self):
        pass

    def guiAnswerCard(self, ease):
        pass

    def guiPlayAudio(self):
        pass

    def guiUndo(self):
        pass

    def guiDeckOverview(self, name):
        pass

    def guiDeckBrowser(self):
        pass

    def guiDeckReview(self, name):
        pass

    def guiImportFile(self, path=None):
        pass

    def guiExitAnki(self):
        pass

    def guiCheckDatabase(self):
        pass

    def addNotes(self, notes):
        pass

    def canAddNotes(self, notes):
        pass

    def canAddNotesWithErrorDetail(self, notes):
        pass

    def exportPackage(self, deck, path, includeSched=False):
        pass

    def importPackage(self, path):
        pass

    def apiReflect(self, scopes=None, actions=None):
        pass

    def send_request(self, action, **params):
        """
        Метод для отправки запросов.
        
        Возвращает: response.json()['result'] или None
        """
        payload = {
            "action": action,
            "version": 6,
            "params": params
        }
        
        try:
            response = requests.post(self.anki_address, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('error'):
                raise Exception(f"AnkiConnect error: {data['error']}")
            return data['result']
        except requests.exceptions.ConnectionError:
            print("❌ Ошибка: Не удалось подключиться к Anki. Убедитесь, что Anki запущен с плагином AnkiConnect.")
            return None
        except requests.exceptions.Timeout:
            print("❌ Ошибка: Таймаут запроса.")
            return None
        except json.JSONDecodeError:
            print("❌ Ошибка: Сервер вернул не-JSON ответ.")
            return None


def hi():
    print(f'hi from {__name__}')


if __name__ == "__main__":
    hi()
    actions = [
    {
        "action": "version",
        "params": {}
    },
    {
        "action": "deckNames",
        "params": {}
    },
    {
        "action": "getProfiles",
        "params": {}
    }
    ]
    anki = AnkiConnect()

    print(anki.send_request("version"))
    print(anki.version())
    print(anki.send_request("deckNames"))
    print(anki.requestPermission('',True))
    print(anki.getProfiles())
    print(anki.getActiveProfile())
    print(anki.loadProfile(anki.getProfiles()[0]))
    anki.sync()
    print(anki.multi(actions))
    print(anki.getNumCardsReviewedToday())
    print(anki.getNumCardsReviewedByDay())
    print(anki.getCollectionStatsHTML())
    print(anki.deckNames())
    print(anki.deckNamesAndIds())
    print(anki.getDecks(['1']))