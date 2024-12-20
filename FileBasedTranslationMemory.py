import sqlite3
import datetime
from StringUtils import StringUtils
from BooleanSettingsWrapper import BooleanSettingsWrapper
from TranslationMemory import TranslationMemory
from Resource import Resource
from DefaultFallbackRecognizer import DefaultFallbackRecognizer

class FileBasedTranslationMemory:
    def __init__(self, tmPath):

        self.tm = None
        # Set file path
        self.FilePath = tmPath
        self._create_connection()
        if self.FilePath.endswith('.sdltm'):
            self._importSdltmFile()

    def destruct(self):
        self._close_connection()

    def _create_connection(self):
        self.conn = sqlite3.connect(self.FilePath)
        self.cursor = self.conn.cursor()

    def _close_connection(self):
        if self.conn:
            self.conn.close()

    def _getParameter(self, name):
        try:
            query = 'SELECT value FROM parameters WHERE translation_memory_id IS NULL AND name = \'' + name + '\''
            self.cursor.execute(query)
            result = self.cursor.fetchone()[0]
        except sqlite3.OperationalError:
            result = ''
        return result

    def _setParameter(self, name, value):
        query = 'DELETE FROM parameters WHERE translation_memory_id IS NULL AND name = \'' + name + '\''
        self.cursor.execute(query)

        if value is not None:
            query = 'INSERT INTO parameters (name, value) VALUES (\'' + name + '\', \'' + value + '\')'
            self.cursor.execute(query)

    def get_resources_write_count(self):
        parameter = self._getParameter('RESWRCNT')
        try:
            result = int(parameter)
        except ValueError:
            return 0
        return result

    #SqliteStorage::GetTm
    def get_tm(self, _id):
        self._check_version()
        query = "SELECT id, guid, name, source_language, target_language, copyright, description, settings, \r\n\t\t\t\tcreation_user, creation_date, expiration_date, fuzzy_indexes, last_recompute_date, last_recompute_size " + self._get_fga_colspec() + self._get_cm_colspec() + " FROM translation_memories WHERE id = " + str(_id)
        tms = self.__get_tms(query)

        tm = None

        if len(tms) > 0:
            tm = tms[0]
        return tm

    #ResourceManager::GetTranslationMemory
    def get_translation_memory(self, _id):
        tm = self.get_tm(_id)
        return tm

    #ResourceManager::GetLanguageResources
    def get_language_resources(self, _id, _include_data):
        return self.get_resources(_id, _include_data)

    #SqliteStorage::GetResources
    def get_resources(self, _id, _include_data):
        self._check_version()
        query = 'SELECT r.id, r.guid, r.type, r.language, r.data \r\n\t\t\t\tFROM resources r INNER JOIN tm_resources tr ON r.id = tr.resource_id\r\n\t\t\t\tWHERE tr.tm_id = ' + str(_id);
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        lst = []
        for row in rows:
            n = int(row[0])
            guid = row[1]
            resource_type = int(row[2])
            language = str(row[3])
            data = None
            if _include_data:
                data = row[4]

            lst.append(Resource(n, guid, resource_type, language, data))

        return lst

    #CallContext::GetAnnotatedTranslationMemory
    #AnnotatedTmManager::GetAnnotatedTranslationMemory
    def get_annotated_translation_memory(self, _id):
        annotated_tm = {}
        annotated_tm['resources_write_count'] = self.get_resources_write_count()
        annotated_tm['language_resources'] = self.get_language_resources(_id, True)
        annotated_tm['tm'] = self.get_translation_memory(_id)
        return annotated_tm

    def _get_cm_colspec(self):
        result = ", 0, " + str(1) + ", 0"
        if self.can_choose_text_context_match_type:
            result = ", data_version, text_context_match_type, id_context_match"
        return result

    def _check_version(self):
        # Check Version
        text = self._getParameter('VERSION')
        createdVersion = self._getParameter('VERSION_CREATED')
        parameter = self._getParameter('TokenDataVersion')

        self.serializesTokens = False

        if parameter is not None:
            try:
                result = int(parameter)
            except ValueError:
                raise Exception('Invalid parameter value \'' + parameter + '\' for parameter TokenDataVersion')

            if result == 0 or result > 1:
                raise Exception('TokenDataVersion value is unsupported: ' + str(result))
            self.serializesTokens = True

        if not text:
            return

        if createdVersion is not None:
            num = StringUtils.compare_ordinal_ignore_case("8.09", createdVersion)
            self.can_report_reindex_required = (num <= 0)
            num = StringUtils.compare_ordinal_ignore_case("8.10", createdVersion)
            self.can_choose_text_context_match_type = (num <= 0)

        num = StringUtils.compare_ordinal_ignore_case("8.06", text)

        if num < 0:
            raise ("ErrorCode.StorageVersionDataNewer")
        if num == 0:
            return

        flag = False

        if text == '8.03':
            self.cursor.execute(
                'CREATE TABLE fuzzy_data(\r\n\ttranslation_memory_id INT NOT NULL CONSTRAINT FK_fi1_tm REFERENCES translation_memories(id) ON DELETE CASCADE,\r\n\ttranslation_unit_id INT NOT NULL,\r\n\tfi1 TEXT,\r\n\tfi2 TEXT,\r\n\tfi4 TEXT,\r\nCONSTRAINT PK_fi1 PRIMARY KEY (\r\n\ttranslation_memory_id, translation_unit_id\r\n)\r\n);')
            self.cursor.execute(
                'INSERT INTO fuzzy_data(translation_memory_id, translation_unit_id, fi1, fi2, fi4)\r\nSELECT x1.translation_memory_id, x1.translation_unit_id, x1.feature fi1, x2.feature fi2, x4.feature fi4\r\nFROM fuzzy_index1 x1\r\n\tINNER JOIN fuzzy_index2 x2 ON (x1.translation_memory_id = x2.translation_memory_id AND \r\n\t\t\t\t   x1.translation_unit_id = x2.translation_unit_id) \r\n\tINNER JOIN fuzzy_index4 x4 ON (x2.translation_memory_id = x4.translation_memory_id AND \r\n\t\t\t\t   x2.translation_unit_id = x4.translation_unit_id)\r\n')
            self.cursor.execute('DROP TABLE fuzzy_index1')
            self.cursor.execute('DROP TABLE fuzzy_index2')
            self.cursor.execute('DROP TABLE fuzzy_index4')

            self._setParameter('VERSION', '8.04')
            text = '8.04'
            flag = True
            self.cursor.execute('VACUUM')

        if text == '8.04':
            self.cursor.execute('ALTER TABLE fuzzy_data ADD COLUMN fi8 TEXT')
            self._setParameter('VERSION', '8.05')
            text = '8.05'
            flag = True

        if text == '8.05':
            self.cursor.execute('ALTER TABLE translation_memories ADD COLUMN flags INT NOT NULL DEFAULT 0')
            self.cursor.execute('ALTER TABLE translation_memories ADD COLUMN tucount INT NOT NULL DEFAULT 0')
            self._updateTuCounts()
            self._setParameter('VERSION', '8.06')
            flag = True

        if flag == False:
            raise ('ErrorCode.StorageVersionDataOutdated')

    #SqliteStorage::SupportsAlignmentData
    def _supports_alignment_data(self):
        parameter = self._getParameter('AlignmentDataVersion')

        if not parameter:
            return False

        try:
            result = int(parameter)
        except ValueError:
            raise Exception('Invalid parameter value \'' + parameter + '\' for parameter AlignmentDataVersion')

        if result == 0 or result > 1:
            raise Exception('AlignmentDataVersion value is unsupported: ' + str(result))

        if not self.serializesTokens:
            raise Exception('TM with alignment data support must also serialize tokens')

        return True

    #SqliteStorage::GetFgaColspec
    def _get_fga_colspec(self):
        result = ', ' + str(0)
        if self._supports_alignment_data():
            result = ', fga_support'
        return result

    def _get_cm_colspec(self):
        result = ', 0, ' + str(1) + ', 0'
        if self.can_choose_text_context_match_type:
            result = ", data_version, text_context_match_type, id_context_match"
        return result

    #SqliteStorage::GetTms(DbCommand cmd)
    def __get_tms(self, query):
        lst = []
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            booleanSettingsWrapper = BooleanSettingsWrapper(row[7])
            expirationDate = None
            if row[10] is not None:
                expirationDate = datetime.datetime.strptime(row[10], '%Y-%m-%d %H:%M:%S')
            desc = None
            if row[5] is not None:
                desc = str(row[5])
            translationMemory = TranslationMemory(
                int(row[0]),
                row[1],
                str(row[2]),
                str(row[3]),
                str(row[4]),
                booleanSettingsWrapper.builtinRecognizer,
                str(row[8]),
                datetime.datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S'),
                desc,
                str(row[6]),
                expirationDate,
                booleanSettingsWrapper.tokenizerFlags,
                booleanSettingsWrapper.wordCountFlags)
            translationMemory.fuzzy_indexes = int(row[11])

            translationMemory.last_recompute_date = None
            if row[12] is not None:
                translationMemory.last_recompute_date = datetime.datetime.strptime(row[12], '%Y-%m-%d %H:%M:%S')
            translationMemory.last_recompute_size = None
            if row[13] is not None:
                translationMemory.last_recompute_size = int(row[13])
            translationMemory.fga_support = int(row[14])
            translationMemory.data_version = int(row[15])
            translationMemory.text_context_match_type = int(row[16])
            translationMemory.id_context_match = bool(row[17])
            translationMemory.can_report_reindex_required = self.can_report_reindex_required
            lst.append(translationMemory)

        return lst

    #SqliteStorage::GetTms()
    def _get_tms(self):
        self._check_version()
        return self.__get_tms('SELECT id, guid, name, source_language, target_language, copyright, description, settings, \r\n\t\t\t\tcreation_user, creation_date, expiration_date, fuzzy_indexes, last_recompute_date, last_recompute_size' + self._get_fga_colspec() + self._get_cm_colspec() + ' FROM translation_memories')

    def _importSdltmFile(self):
        lst = self._get_tms()
        self.tm = lst[0]

    def search_translation_unit(self, settings, tu):
        annotated_translation_memory = self.get_annotated_translation_memory(self.tm.id)
        annotated_translation_unit = {}
        annotated_translation_unit['translation_unit'] = tu
        recognizer = DefaultFallbackRecognizer(annotated_translation_memory['language_resources'])
        recognizer.recognize('Our Belief', 0,False)
