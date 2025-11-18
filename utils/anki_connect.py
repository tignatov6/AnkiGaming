import requests

class AnkiConnect():
    def __init__(self):
        pass

    def version(self):
        pass

    def requestPermission(self, origin, allowed):
        pass

    def getProfiles(self):
        pass

    def getActiveProfile(self):
        pass

    def loadProfile(self, name):
        pass

    def sync(self):
        pass

    def multi(self, actions):
        pass

    def getNumCardsReviewedToday(self):
        pass

    def getNumCardsReviewedByDay(self):
        pass

    def getCollectionStatsHTML(self, wholeCollection=True):
        pass

    def deckNames(self):
        pass

    def deckNamesAndIds(self):
        pass

    def getDecks(self, cards):
        pass

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

def hi():
    print(f'hi from {__name__}')


if __name__ == "__main__":
    hi()