import sqlite3
import datetime
from StringUtils import StringUtils
from BooleanSettingsWrapper import BooleanSettingsWrapper
from TranslationMemory import TranslationMemory


class FileBasedTranslationMemory:
    def __init__(self, tmPath):
        # Set file path
        self.FilePath = tmPath
        if self.FilePath.endswith('.sdltm'):
            self._importSdltmFile()

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

    def _get_cm_colspec(self):
        result = ", 0, " + str(1) + ", 0"
        if self.can_choose_text_context_match_type:
            result = ", data_version, text_context_match_type, id_context_match"
        return result

    def _checkVersion(self):
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
        list = []
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
            list.append(translationMemory)

        return list

    #SqliteStorage::GetTms()
    def _get_tms(self):
        self._checkVersion()
        return self.__get_tms('SELECT id, guid, name, source_language, target_language, copyright, description, settings, \r\n\t\t\t\tcreation_user, creation_date, expiration_date, fuzzy_indexes, last_recompute_date, last_recompute_size' + self._get_fga_colspec() + self._get_cm_colspec() + ' FROM translation_memories')

    def _importSdltmFile(self):
        try:
            conn = sqlite3.connect(self.FilePath)
            self.cursor = conn.cursor()
            self._get_tms()

        except sqlite3.Error as e:
            print(f"Error reading SDLTM file: {e}")
            return []
        finally:
            if conn:
                conn.close()