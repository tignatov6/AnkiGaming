import requests
import json

def hi():
    print(f'hi from {__name__}')

class AnkiConnect():
    """
    Класс-обертка для взаимодействия с Anki через плагин AnkiConnect.
    """
    def __init__(self, anki_address='http://localhost:8765'):
        self.anki_address = anki_address

    def version(self):
        """
        Получает версию API AnkiConnect.
        :return: Строка с номером версии (например, '6').
        """
        return self.send_request("version")

    def requestPermission(self, origin, allowed):
        """
        Запрашивает разрешение на доступ к API (используется для CORS/безопасности).
        :param origin: Источник запроса (например, 'localhost').
        :param allowed: Разрешить (True) или запретить (False).
        :return: Кортеж (status, requireApikey, version).
        """
        result = self.send_request("requestPermission", origin=origin, allowed=allowed)
        return result['permission'], result['requireApikey'], result['version']
        
    def getProfiles(self):
        """
        Получает список всех доступных профилей в Anki.
        :return: Список строк (имен профилей).
        """
        return self.send_request('getProfiles')

    def getActiveProfile(self):
        """
        Получает имя текущего активного профиля.
        :return: Имя профиля (строка).
        """
        return self.send_request("getActiveProfile")

    def loadProfile(self, name):
        """
        Переключает Anki на указанный профиль.
        :param name: Имя профиля.
        :return: True, если переключение успешно.
        """
        return self.send_request("loadProfile", name=name)

    def sync(self):
        """
        Запускает синхронизацию с AnkiWeb.
        Примечание: Требует, чтобы пользователь был залогинен в Anki.
        """
        return self.send_request("sync")

    def multi(self, actions):
        """
        Выполняет несколько действий в одном HTTP-запросе (пакетная обработка).
        :param actions: Список словарей, где каждый словарь описывает действие 
                        (напр. {'action': 'deckNames', 'params': {}}).
        :return: Список результатов для каждого действия в том же порядке.
        """
        return self.send_request("multi", actions=actions)

    def getNumCardsReviewedToday(self):
        """
        Возвращает количество карточек, пройденных сегодня.
        :return: Целое число (количество).
        """
        return self.send_request("getNumCardsReviewedToday")

    def getNumCardsReviewedByDay(self):
        """
        Возвращает статистику просмотров по дням.
        :return: Список списков вида [["2023-01-01", 50], ...].
        """
        return self.send_request("getNumCardsReviewedByDay")

    def getCollectionStatsHTML(self, wholeCollection=True):
        """
        Получает HTML-код страницы статистики (как в окне "Статистика" в Anki).
        :param wholeCollection: True для всей коллекции, False для текущей колоды.
        :return: Строка с HTML.
        """
        return self.send_request("getCollectionStatsHTML", wholeCollection=wholeCollection)

    def deckNames(self):
        """
        Получает список имен всех колод.
        :return: Список строк.
        """
        return self.send_request("deckNames")

    def deckNamesAndIds(self):
        """
        Получает имена колод и их ID.
        :return: Словарь { "Имя колоды": ID_колоды }.
        """
        return self.send_request("deckNamesAndIds")

    def getDecks(self, cards):
        """
        Определяет, в каких колодах находятся указанные карты.
        :param cards: Список ID карт.
        :return: Словарь { "Имя колоды": [список ID карт] }.
        """
        return self.send_request("getDecks", cards=cards)

    def createDeck(self, deck):
        """
        Создаёт новую колоду (или возвращает ID существующей).
        :param deck: Имя новой колоды.
        :return: ID колоды (int).
        """
        return self.send_request("createDeck", deck=deck)

    def changeDeck(self, cards, deck):
        """
        Перемещает указанные карты в другую колоду.
        :param cards: Список ID карт.
        :param deck: Имя целевой колоды.
        """
        return self.send_request("changeDeck", cards=cards, deck=deck)

    def deleteDecks(self, decks, cardsToo=False):
        """
        Удаляет указанные колоды.
        :param decks: Список имен колод.
        :param cardsToo: Если True, удаляет карты внутри колод. Если False и колода не пуста, вернет ошибку.
        """
        return self.send_request("deleteDecks", decks=decks, cardsToo=cardsToo)

    def getDeckConfig(self, deck):
        """
        Получает настройки (options group) для указанной колоды.
        :param deck: Имя колоды.
        :return: Словарь с настройками.
        """
        return self.send_request("getDeckConfig", deck=deck)

    def saveDeckConfig(self, config):
        """
        Сохраняет (обновляет) конфигурацию колоды.
        :param config: Словарь конфигурации (должен содержать 'id').
        :return: True при успехе.
        """
        return self.send_request("saveDeckConfig", config=config)

    def setDeckConfigId(self, decks, configId):
        """
        Применяет определенную группу настроек (Config ID) к списку колод.
        :param decks: Список имен колод.
        :param configId: ID группы настроек.
        :return: True при успехе.
        """
        return self.send_request("setDeckConfigId", decks=decks, configId=configId)

    def cloneDeckConfigId(self, name, cloneFrom='1'):
        """
        Клонирует группу настроек.
        :param name: Имя новой группы настроек.
        :param cloneFrom: ID исходной группы (строка или число).
        :return: ID новой группы настроек.
        """
        return self.send_request("cloneDeckConfigId", name=name, cloneFrom=cloneFrom)

    def removeDeckConfigId(self, configId):
        """
        Удаляет группу настроек.
        :param configId: ID группы настроек.
        :return: True при успехе.
        """
        return self.send_request("removeDeckConfigId", configId=configId)

    def getDeckStats(self, decks):
        """
        Получает статистику (количество новых, изучаемых, повторяемых карт) для списка колод.
        :param decks: Список имен колод.
        :return: Словарь { "ID_колоды": {статистика} }.
        """
        return self.send_request("getDeckStats", decks=decks)

    def storeMediaFile(self, filename, data=None, path=None, url=None, skipHash=None, deleteExisting=True):
        """
        Загружает медиафайл в папку collection.media.
        Нужно указать ОДИН из параметров: data (base64), path (локальный путь) или url.
        :param filename: Имя файла, под которым он сохранится в Anki.
        :param data: Base64-кодированное содержимое файла.
        :param path: Путь к локальному файлу для загрузки.
        :param url: URL для скачивания файла.
        :return: Имя сохраненного файла или None (если пропущено по хешу).
        """
        return self.send_request("storeMediaFile", filename=filename, data=data, path=path, url=url, skipHash=skipHash, deleteExisting=deleteExisting)

    def retrieveMediaFile(self, filename):
        """
        Получает содержимое медиафайла.
        :param filename: Имя файла.
        :return: Base64 строка содержимого.
        """
        return self.send_request("retrieveMediaFile", filename=filename)

    def getMediaFilesNames(self, pattern='*'):
        """
        Получает список файлов в папке медиа по паттерну.
        :param pattern: Шаблон поиска (например, '*.jpg').
        :return: Список имен файлов.
        """
        return self.send_request("getMediaFilesNames", pattern=pattern)

    def deleteMediaFile(self, filename):
        """
        Удаляет файл из папки медиа.
        :param filename: Имя файла.
        """
        return self.send_request("deleteMediaFile", filename=filename)

    def getMediaDirPath(self):
        """
        Получает полный локальный путь к папке collection.media.
        :return: Строка пути.
        """
        return self.send_request("getMediaDirPath")

    def addNote(self, note):
        """
        Создает новую заметку (Note).
        :param note: Словарь с описанием заметки:
                     {
                       "deckName": "Default",
                       "modelName": "Basic",
                       "fields": {"Front": "...", "Back": "..."},
                       "tags": ["tag1", "tag2"]
                     }
        :return: ID созданной заметки (int).
        """
        return self.send_request("addNote", note=note)

    def canAddNote(self, note):
        """
        Проверяет, можно ли добавить заметку (не является ли она дубликатом).
        :param note: Словарь заметки (см. addNote).
        :return: True, если можно добавить.
        """
        return self.send_request("canAddNote", note=note)

    def canAddNoteWithErrorDetail(self, note):
        """
        Проверяет возможность добавления с детализацией ошибки.
        :return: Словарь вида {'canAdd': False, 'error': '...'}
        """
        return self.send_request("canAddNoteWithErrorDetail", note=note)

    def updateNoteFields(self, note):
        """
        Обновляет поля существующей заметки.
        :param note: Словарь { "id": note_id, "fields": { "Field": "New Value" } }.
        """
        return self.send_request("updateNoteFields", note=note)

    def updateNote(self, note):
        """
        Обновляет поля и/или теги заметки.
        :param note: Словарь { "id": ..., "fields": {...}, "tags": [...] }.
        """
        return self.send_request("updateNote", note=note)

    def updateNoteModel(self, note):
        """
        Меняет тип записи (Model) для заметки.
        :param note: Словарь { "id": ..., "modelName": "NewModel", "fields": {...}, "tags": [...] }.
        """
        return self.send_request("updateNoteModel", note=note)

    def updateNoteTags(self, note, tags):
        """
        Полностью заменяет теги заметки на переданный список.
        :param note: ID заметки.
        :param tags: Список новых тегов.
        """
        return self.send_request("updateNoteTags", note=note, tags=tags)

    def getNoteTags(self, note):
        """
        Получает список тегов для указанной заметки.
        :param note: ID заметки.
        :return: Список тегов.
        """
        return self.send_request("getNoteTags", note=note)

    def addTags(self, notes, tags, add=True):
        """
        Добавляет теги к списку заметок.
        :param notes: Список ID заметок.
        :param tags: Строка (теги через пробел).
        """
        return self.send_request("addTags", notes=notes, tags=tags, add=add)

    def removeTags(self, notes, tags):
        """
        Удаляет теги у списка заметок.
        :param notes: Список ID заметок.
        :param tags: Строка (теги через пробел).
        """
        return self.send_request("removeTags", notes=notes, tags=tags)

    def getTags(self):
        """
        Получает список всех тегов, используемых в коллекции.
        :return: Список строк.
        """
        return self.send_request("getTags")

    def clearUnusedTags(self):
        """
        Удаляет из базы неиспользуемые теги.
        """
        return self.send_request("clearUnusedTags")

    def replaceTags(self, notes, tag_to_replace, replace_with_tag):
        """
        Заменяет один тег на другой в указанных заметках.
        :param notes: Список ID заметок.
        """
        return self.send_request("replaceTags", notes=notes, tag_to_replace=tag_to_replace, replace_with_tag=replace_with_tag)

    def replaceTagsInAllNotes(self, tag_to_replace, replace_with_tag):
        """
        Заменяет один тег на другой во всей коллекции.
        """
        return self.send_request("replaceTagsInAllNotes", tag_to_replace=tag_to_replace, replace_with_tag=replace_with_tag)

    def setEaseFactors(self, cards, easeFactors):
        """
        Устанавливает коэффициент легкости (Ease Factor) для карт.
        :param cards: Список ID карт.
        :param easeFactors: Список значений (напр. [2500, 2600]). 2500 = 250%.
        :return: Список булевых значений успеха.
        """
        return self.send_request("setEaseFactors", cards=cards, easeFactors=easeFactors)

    def setSpecificValueOfCard(self, card, keys, newValues, warning_check=False):
        """
        Прямое изменение полей в таблице `cards` (опасно!).
        :param card: ID карты.
        :param keys: Список имен колонок (напр. ["reps", "lapses"]).
        :param newValues: Список новых значений.
        """
        return self.send_request("setSpecificValueOfCard", card=card, keys=keys, newValues=newValues, warning_check=warning_check)

    def getEaseFactors(self, cards):
        """
        Получает Ease Factor для списка карт.
        :return: Список значений.
        """
        return self.send_request("getEaseFactors", cards=cards)

    def suspend(self, cards, suspend=True):
        """
        Приостанавливает (suspend) карты (исключает из обзора) или возвращает их.
        :param cards: Список ID карт.
        :param suspend: True - приостановить (желтые), False - вернуть.
        :return: True при успехе.
        """
        return self.send_request("suspend", cards=cards, suspend=suspend)

    def unsuspend(self, cards):
        """
        Снимает статус Suspend с карт.
        :param cards: Список ID карт.
        """
        return self.send_request("unsuspend", cards=cards)

    def suspended(self, card):
        """
        Проверяет, приостановлена ли карта.
        :param card: ID карты.
        :return: True/False.
        """
        return self.send_request("suspended", card=card)

    def areSuspended(self, cards):
        """
        Проверяет статус Suspend для списка карт.
        :return: Список Nullable Boolean (True/False/None).
        """
        return self.send_request("areSuspended", cards=cards)

    def areDue(self, cards):
        """
        Проверяет, нужно ли учить карты сейчас (Due).
        :param cards: Список ID карт.
        :return: Список булевых значений.
        """
        return self.send_request("areDue", cards=cards)

    def getIntervals(self, cards, complete=False):
        """
        Получает текущие интервалы (в днях) для карт.
        :param cards: Список ID карт.
        :param complete: Если True, возвращает все исторические интервалы.
        :return: Список чисел.
        """
        return self.send_request("getIntervals", cards=cards, complete=complete)

    def modelNames(self):
        """
        Получает список имен всех типов записей (Models).
        :return: Список строк.
        """
        return self.send_request("modelNames")

    def createModel(self, modelName, inOrderFields, cardTemplates, css=None, isCloze=False):
        """
        Создает новый тип записи (Model).
        :param modelName: Имя модели.
        :param inOrderFields: Список имен полей.
        :param cardTemplates: Список словарей шаблонов (Front/Back).
        :return: Объект созданной модели.
        """
        return self.send_request("createModel", modelName=modelName, inOrderFields=inOrderFields, cardTemplates=cardTemplates, css=css, isCloze=isCloze)

    def modelNamesAndIds(self):
        """
        Получает словарь { "Имя модели": ID }.
        """
        return self.send_request("modelNamesAndIds")

    def findModelsById(self, modelIds):
        """
        Находит объекты моделей по их ID.
        """
        return self.send_request("findModelsById", modelIds=modelIds)

    def findModelsByName(self, modelNames):
        """
        Находит объекты моделей по их именам.
        """
        return self.send_request("findModelsByName", modelNames=modelNames)

    def modelNameFromId(self, modelId):
        """
        Получает имя модели по ID.
        """
        return self.send_request("modelNameFromId", modelId=modelId)

    def modelFieldNames(self, modelName):
        """
        Получает список имен полей для указанной модели.
        :param modelName: Имя модели.
        :return: Список строк.
        """
        return self.send_request("modelFieldNames", modelName=modelName)

    def modelFieldDescriptions(self, modelName):
        """
        Получает описания полей (подсказки в редакторе).
        """
        return self.send_request("modelFieldDescriptions", modelName=modelName)

    def modelFieldFonts(self, modelName):
        """
        Получает настройки шрифтов для полей.
        """
        return self.send_request("modelFieldFonts", modelName=modelName)

    def modelFieldsOnTemplates(self, modelName):
        """
        Показывает, какие поля используются на каких шаблонах карт.
        """
        return self.send_request("modelFieldsOnTemplates", modelName=modelName)

    def modelTemplates(self, modelName):
        """
        Получает содержимое шаблонов карт (Front/Back HTML).
        :return: Словарь { "Имя карты": {"Front": "...", "Back": "..."} }.
        """
        return self.send_request("modelTemplates", modelName=modelName)

    def modelStyling(self, modelName):
        """
        Получает CSS стили модели.
        :return: Словарь {"css": "..."}.
        """
        return self.send_request("modelStyling", modelName=modelName)

    def updateModelTemplates(self, model):
        """
        Обновляет HTML шаблоны для модели.
        :param model: Словарь { "name": "ModelName", "templates": {...} }.
        """
        return self.send_request("updateModelTemplates", model=model)

    def updateModelStyling(self, model):
        """
        Обновляет CSS стили модели.
        :param model: Словарь { "name": "ModelName", "css": "..." }.
        """
        return self.send_request("updateModelStyling", model=model)

    def findAndReplaceInModels(self, modelName, findText, replaceText, front=True, back=True, css=True):
        """
        Найти и заменить текст в шаблонах или CSS моделей.
        """
        return self.send_request("findAndReplaceInModels", modelName=modelName, findText=findText, replaceText=replaceText, front=front, back=back, css=css)

    def modelTemplateRename(self, modelName, oldTemplateName, newTemplateName):
        """Переименовывает шаблон карточки в модели."""
        return self.send_request("modelTemplateRename", modelName=modelName, oldTemplateName=oldTemplateName, newTemplateName=newTemplateName)

    def modelTemplateReposition(self, modelName, templateName, index):
        """Изменяет порядок шаблонов карточек."""
        return self.send_request("modelTemplateReposition", modelName=modelName, templateName=templateName, index=index)

    def modelTemplateAdd(self, modelName, template):
        """Добавляет новый шаблон карточки в модель."""
        return self.send_request("modelTemplateAdd", modelName=modelName, template=template)

    def modelTemplateRemove(self, modelName, templateName):
        """Удаляет шаблон карточки из модели."""
        return self.send_request("modelTemplateRemove", modelName=modelName, templateName=templateName)

    def modelFieldRename(self, modelName, oldFieldName, newFieldName):
        """Переименовывает поле в модели."""
        return self.send_request("modelFieldRename", modelName=modelName, oldFieldName=oldFieldName, newFieldName=newFieldName)

    def modelFieldReposition(self, modelName, fieldName, index):
        """Изменяет порядок полей в модели."""
        return self.send_request("modelFieldReposition", modelName=modelName, fieldName=fieldName, index=index)

    def modelFieldAdd(self, modelName, fieldName, index=None):
        """Добавляет новое поле в модель."""
        return self.send_request("modelFieldAdd", modelName=modelName, fieldName=fieldName, index=index)

    def modelFieldRemove(self, modelName, fieldName):
        """Удаляет поле из модели."""
        return self.send_request("modelFieldRemove", modelName=modelName, fieldName=fieldName)

    def modelFieldSetFont(self, modelName, fieldName, font):
        """Устанавливает шрифт для поля."""
        return self.send_request("modelFieldSetFont", modelName=modelName, fieldName=fieldName, font=font)

    def modelFieldSetFontSize(self, modelName, fieldName, fontSize):
        """Устанавливает размер шрифта для поля."""
        return self.send_request("modelFieldSetFontSize", modelName=modelName, fieldName=fieldName, fontSize=fontSize)

    def modelFieldSetDescription(self, modelName, fieldName, description):
        """Устанавливает описание (description) для поля."""
        return self.send_request("modelFieldSetDescription", modelName=modelName, fieldName=fieldName, description=description)

    def deckNameFromId(self, deckId):
        """
        Получает имя колоды по её ID.
        :return: Имя колоды (строка).
        """
        return self.send_request("deckNameFromId", deckId=deckId)

    def findNotes(self, query=None):
        """
        Ищет заметки по запросу (как в браузере Anki).
        :param query: Строка запроса (напр. "deck:Default tag:hard").
        :return: Список ID заметок.
        """
        return self.send_request("findNotes", query=query)

    def findCards(self, query=None):
        """
        Ищет карты по запросу.
        :param query: Строка запроса (напр. "is:due").
        :return: Список ID карт.
        """
        return self.send_request("findCards", query=query)

    def cardsInfo(self, cards):
        """
        Возвращает детальную информацию о списке карт.
        :param cards: Список ID карт.
        :return: Список словарей с полями, интервалами, колодой и т.д.
        """
        return self.send_request("cardsInfo", cards=cards)

    def cardsModTime(self, cards):
        """
        Получает время последней модификации карт.
        :return: Список словарей { "cardId": id, "mod": timestamp }.
        """
        return self.send_request("cardsModTime", cards=cards)

    def forgetCards(self, cards):
        """
        Сбрасывает прогресс карт (делает их "Новыми").
        :param cards: Список ID карт.
        """
        return self.send_request("forgetCards", cards=cards)

    def relearnCards(self, cards):
        """
        Переводит карты в режим переобучения (как будто нажали "Снова").
        :param cards: Список ID карт.
        """
        return self.send_request("relearnCards", cards=cards)

    def answerCards(self, answers):
        """
        Отвечает на карты (имитирует нажатие кнопок 1-4).
        :param answers: Список словарей [{ "cardId": 123, "ease": 3 }, ...].
                        ease: 1(Again), 2(Hard), 3(Good), 4(Easy).
        """
        return self.send_request("answerCards", answers=answers)

    def cardReviews(self, deck, startID):
        """
        Получает историю пересмотров для колоды начиная с определенного ID (timestamp).
        """
        return self.send_request("cardReviews", deck=deck, startID=startID)

    def getReviewsOfCards(self, cards):
        """
        Получает историю пересмотров для конкретных карт.
        :param cards: Список ID карт.
        :return: Словарь { "ID_карты": [список отзывов] }.
        """
        return self.send_request("getReviewsOfCards", cards=cards)

    def setDueDate(self, cards, days):
        """
        Переносит срок пересмотра карт (Reschedule).
        :param days: "0" - сегодня, "1" - завтра, "1-7" - случайно от 1 до 7 дней.
        """
        return self.send_request("setDueDate", cards=cards, days=days)

    def reloadCollection(self):
        """
        Принудительно перезагружает коллекцию в Anki (сброс кэша).
        """
        return self.send_request("reloadCollection")

    def getLatestReviewID(self, deck):
        """
        Получает ID (timestamp) последнего пересмотра в колоде.
        """
        return self.send_request("getLatestReviewID", deck=deck)

    def insertReviews(self, reviews):
        """
        Вставляет историю пересмотров напрямую в базу (продвинутое использование).
        """
        return self.send_request("insertReviews", reviews=reviews)

    def notesInfo(self, notes=None, query=None):
        """
        Возвращает детальную информацию о заметках (по ID или запросу).
        """
        return self.send_request("notesInfo", notes=notes, query=query)

    def notesModTime(self, notes):
        """
        Получает время модификации заметок.
        """
        return self.send_request("notesModTime", notes=notes)

    def deleteNotes(self, notes):
        """
        Удаляет заметки (и, соответственно, карты из них).
        :param notes: Список ID заметок.
        """
        return self.send_request("deleteNotes", notes=notes)

    def removeEmptyNotes(self):
        """
        Удаляет заметки, у которых нет содержимого (пустые поля).
        """
        return self.send_request("removeEmptyNotes")

    def cardsToNotes(self, cards):
        """
        Получает ID заметок, которым принадлежат указанные карты.
        :param cards: Список ID карт.
        :return: Список ID заметок.
        """
        return self.send_request("cardsToNotes", cards=cards)

    def guiBrowse(self, query=None, reorderCards=None):
        """
        Открывает окно браузера Anki с указанным поисковым запросом.
        """
        return self.send_request("guiBrowse", query=query, reorderCards=reorderCards)

    def guiEditNote(self, note):
        """
        Открывает окно редактирования для указанной заметки (ID).
        """
        return self.send_request("guiEditNote", note=note)

    def guiSelectNote(self, note):
        """
        Выделяет заметку в браузере.
        """
        return self.send_request("guiSelectNote", note=note)

    def guiSelectCard(self, card):
        """
        Выделяет карту в браузере.
        """
        return self.send_request("guiSelectCard", card=card)

    def guiSelectedNotes(self):
        """
        Возвращает список ID заметок, выделенных в текущий момент в браузере.
        """
        return self.send_request("guiSelectedNotes")

    def guiAddCards(self, note=None):
        """
        Открывает диалог "Добавить карты".
        :param note: Если передан, предварительно заполняет поля.
        """
        return self.send_request("guiAddCards", note=note)

    def guiReviewActive(self):
        """
        Проверяет, открыто ли окно обзора (Reviewer) сейчас.
        :return: True/False.
        """
        return self.send_request("guiReviewActive")

    def guiCurrentCard(self):
        """
        Получает информацию о текущей карте в окне обзора.
        :return: Словарь с данными карты или ошибка, если обзор не активен.
        """
        return self.send_request("guiCurrentCard")

    def guiStartCardTimer(self):
        """
        Запускает таймер ответа на карту (в GUI).
        """
        return self.send_request("guiStartCardTimer")

    def guiShowQuestion(self):
        """
        Показывает вопрос текущей карты (в GUI).
        """
        return self.send_request("guiShowQuestion")

    def guiShowAnswer(self):
        """
        Показывает ответ текущей карты (в GUI).
        """
        return self.send_request("guiShowAnswer")

    def guiAnswerCard(self, ease):
        """
        Нажимает кнопку ответа в GUI.
        :param ease: 1 (Снова) - 4 (Легко).
        """
        return self.send_request("guiAnswerCard", ease=ease)

    def guiPlayAudio(self):
        """
        Воспроизводит аудио текущей карты.
        """
        return self.send_request("guiPlayAudio")

    def guiUndo(self):
        """
        Выполняет действие "Отмена" (Ctrl+Z) в Anki.
        """
        return self.send_request("guiUndo")

    def guiDeckOverview(self, name):
        """
        Переходит на экран обзора колоды.
        :param name: Имя колоды.
        """
        return self.send_request("guiDeckOverview", name=name)

    def guiDeckBrowser(self):
        """
        Переходит на главный экран со списком колод.
        """
        return self.send_request("guiDeckBrowser")

    def guiDeckReview(self, name):
        """
        Запускает обзор (учебу) для указанной колоды.
        """
        return self.send_request("guiDeckReview", name=name)

    def guiImportFile(self, path=None):
        """
        Открывает диалог импорта файла.
        :param path: Путь к файлу (опционально).
        """
        return self.send_request("guiImportFile", path=path)

    def guiExitAnki(self):
        """
        Корректно закрывает приложение Anki.
        """
        return self.send_request("guiExitAnki")

    def guiCheckDatabase(self):
        """
        Запускает проверку базы данных (Check Database).
        """
        return self.send_request("guiCheckDatabase")

    def addNotes(self, notes):
        """
        Массовое добавление заметок.
        :param notes: Список словарей заметок.
        :return: Список ID созданных заметок.
        """
        return self.send_request("addNotes", notes=notes)

    def canAddNotes(self, notes):
        """
        Массовая проверка возможности добавления заметок.
        :return: Список булевых значений.
        """
        return self.send_request("canAddNotes", notes=notes)

    def canAddNotesWithErrorDetail(self, notes):
        """
        Массовая проверка с детализацией ошибок.
        """
        return self.send_request("canAddNotesWithErrorDetail", notes=notes)

    def exportPackage(self, deck, path, includeSched=False):
        """
        Экспортирует колоду в файл .apkg.
        :param deck: Имя колоды.
        :param path: Путь для сохранения файла.
        :param includeSched: Включать ли историю пересмотров.
        """
        return self.send_request("exportPackage", deck=deck, path=path, includeSched=includeSched)

    def importPackage(self, path):
        """
        Импортирует файл .apkg.
        :param path: Путь к файлу.
        """
        return self.send_request("importPackage", path=path)

    def apiReflect(self, scopes=None, actions=None):
        """
        Служебный метод для получения списка доступных методов API.
        """
        return self.send_request("apiReflect", scopes=scopes, actions=actions)

    def send_request(self, action, **params):
        """
        Внутренний метод для отправки HTTP POST запросов к AnkiConnect.
        :param action: Название метода API (напр. "version").
        :param params: Параметры метода (kwargs).
        :return: Значение поля 'result' из JSON-ответа или None при ошибке.
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
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            return None
        
    def get_next_scheduled_card(self, deck_name):
        """
        Получает следующую карточку из колоды, которую Anki показал бы пользователю.
        
        Args:
            deck_name (str): Имя колоды
            
        Returns:
            dict or None: Данные карточки (question, answer, fields и т.д.) или None, 
                        если в колоде нет карточек для повторения
        """
        import time
        
        # 1. Запускаем режим обзора - это заставляет планировщик Anki выбрать следующую карточку
        #    из очереди (учитывая learning/review/new cards, лимиты и burying)
        self.guiDeckReview(deck_name)
        
        # 3. Получаем текущую карточку, которую выбрал планировщик
        card_info = self.guiCurrentCard()
        
        if not card_info:
            print(f"В колоде '{deck_name}' нет карточек для повторения.")
            return None
            
        return card_info


if __name__ == "__main__":
    print(f"--- Запуск тестов модуля {__name__} ---")
    
    anki = AnkiConnect()
    
    # 1. Основные проверки
    print("\n--- 1. Basic Info ---")
    print(f"Version: {anki.version()}")
    # Permission запрос (обычно возвращает None, если уже разрешено или работает на localhost без авторизации)
    print(f"Permission: {anki.requestPermission('localhost', True)}")
    print(f"Profiles: {anki.getProfiles()}")
    print(f"Active Profile: {anki.getActiveProfile()}")
    
    # 2. Статистика
    print("\n--- 2. Stats ---")
    print(f"Cards Reviewed Today: {anki.getNumCardsReviewedToday()}")
    print(f"Reviewed By Day: {anki.getNumCardsReviewedByDay()}") # Может быть длинный вывод
    
    # 3. Колоды (Decks)
    print("\n--- 3. Decks ---")
    deck_names = anki.deckNames()
    print(f"Deck Names: {deck_names}")
    print(f"Deck Names & IDs: {anki.deckNamesAndIds()}")
    
    if deck_names:
        test_deck = deck_names[0]
        print(f"Getting Stats for deck '{test_deck}': {anki.getDeckStats([test_deck])}")
        print(f"Getting Config for deck '{test_deck}': {anki.getDeckConfig(test_deck)}")
        anki.createDeck("TestDeckFromPython")
        anki.deleteDecks(["TestDeckFromPython"], cardsToo=True)
        
    # 4. Модели (Models)
    print("\n--- 4. Models ---")
    model_names = anki.modelNames()
    print(f"Model Names: {model_names}")
    if model_names:
        test_model = model_names[0]
        print(f"Fields for '{test_model}': {anki.modelFieldNames(test_model)}")
        print(f"Templates for '{test_model}': {anki.modelTemplates(test_model)}")
        print(f"Styling for '{test_model}': {anki.modelStyling(test_model)}")
        
    # 5. Карточки и Заметки (Cards & Notes)
    print("\n--- 5. Cards & Notes ---")
    # Найдем несколько карточек для теста
    found_cards = anki.findCards("is:new") # Ищем новые карты
    if not found_cards:
        found_cards = anki.findCards("") # Или любые карты
        
    if found_cards:
        # Берем топ-3 для теста
        test_cards = found_cards[:3]
        print(f"Found Cards IDs: {test_cards}")
        
        print(f"Cards Info: {anki.cardsInfo(test_cards)}")
        print(f"Cards Mod Time: {anki.cardsModTime(test_cards)}")
        print(f"Are Due?: {anki.areDue(test_cards)}")
        print(f"Are Suspended?: {anki.areSuspended(test_cards)}")
        print(f"Get Intervals: {anki.getIntervals(test_cards)}")
        
        # Получим Notes из Cards
        notes_from_cards = anki.cardsToNotes(test_cards)
        print(f"Notes from Cards: {notes_from_cards}")
        
        if notes_from_cards:
            print(f"Notes Info: {anki.notesInfo(notes=notes_from_cards)}")
            print(f"Note Tags: {anki.getNoteTags(notes_from_cards[0])}")
    else:
        print("Карточки не найдены, пропуск тестов с карточками.")

    # 6. GUI (Требует открытого окна Anki)
    print("\n--- 6. GUI Operations (Check Anki Window) ---")
    anki.guiDeckBrowser()
    anki.guiCheckDatabase()
    print("GUI tests executed (commented out by default to avoid switching screens).")

    # 7. Media
    print("\n--- 7. Media ---")
    print(f"Media Dir: {anki.getMediaDirPath()}")
    files = anki.getMediaFilesNames(pattern="*.jpg")
    print(f"Found JPGs: {len(files) if files else 0}")

    # 8. Пример добавления заметки (Закомментировано для безопасности)
    """
    if model_names and deck_names:
        new_note = {
            "deckName": deck_names[0],
            "modelName": model_names[0],
            "fields": {
                # Замените на реальные поля вашей модели
                # "Front": "test front", 
                # "Back": "test back"
            },
            "tags": ["anki_connect_test"]
        }
        # print(f"Can add note?: {anki.canAddNote(new_note)}")
        # note_id = anki.addNote(new_note)
        # print(f"Added Note ID: {note_id}")
    """

    # 9. Multi Action Test
    print("\n--- 9. Multi Action ---")
    actions = [
        {"action": "version"},
        {"action": "deckNames"}
    ]
    print(f"Multi result: {anki.multi(actions)}")
    
    # 10. Sync
    print("\n--- 10. Sync ---")
    anki.sync()
    print("Sync command sent.")
    
    print("\n--- Тесты завершены ---")