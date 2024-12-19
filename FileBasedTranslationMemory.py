import sqlite3
from StringUtils import StringUtils
from BooleanSettingsWrapper import BooleanSettingsWrapper

class FileBasedTranslationMemory:
    def __init__(self, tmPath):
        # Set file path
        self.FilePath = tmPath
        if self.FilePath.endswith('.sdltm'):
            self._importSdltmFile()

    def _getParameter(self, cursor, name):
        try:
            query = 'SELECT value FROM parameters WHERE translation_memory_id IS NULL AND name = \'' + name + '\''
            cursor.execute(query)
            result = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            result = ''
        return result

    def _setParameter(self, cursor, name, value):
        query = 'DELETE FROM parameters WHERE translation_memory_id IS NULL AND name = \'' + name + '\''
        cursor.execute(query)

        if value is not None:
            query = 'INSERT INTO parameters (name, value) VALUES (\'' + name + '\', \'' + value + '\')'
            cursor.execute(query)

    def _get_cm_colspec(self):
        result = ", 0, " + str(1) + ", 0"
        if self._canChooseTextContextMatchType:
            result = ", data_version, text_context_match_type, id_context_match"
        return result

    def _checkVersion(self, cursor):
        # Check Version
        text = self._getParameter(cursor, 'VERSION')
        createdVersion = self._getParameter(cursor, 'VERSION_CREATED')
        parameter = self._getParameter(cursor, 'TokenDataVersion')

        self._serializesTokens = False

        if parameter is not None:
            try:
                result = int(parameter)
            except ValueError:
                raise Exception('Invalid parameter value \'' + parameter + '\' for parameter TokenDataVersion')

            if result == 0 or result > 1:
                raise Exception('TokenDataVersion value is unsupported: ' + str(result))
            self._serializesTokens = True

        if not text:
            return

        if createdVersion is not None:
            num = StringUtils.compare_ordinal_ignore_case("8.09", createdVersion)
            self._canReportReindexRequired = (num <= 0)
            num = StringUtils.compare_ordinal_ignore_case("8.10", createdVersion)
            self._canChooseTextContextMatchType = (num <= 0)

        num = StringUtils.compare_ordinal_ignore_case("8.06", text)

        if num < 0:
            raise ("ErrorCode.StorageVersionDataNewer")
        if num == 0:
            return

        flag = False

        if text == '8.03':
            cursor.execute(
                'CREATE TABLE fuzzy_data(\r\n\ttranslation_memory_id INT NOT NULL CONSTRAINT FK_fi1_tm REFERENCES translation_memories(id) ON DELETE CASCADE,\r\n\ttranslation_unit_id INT NOT NULL,\r\n\tfi1 TEXT,\r\n\tfi2 TEXT,\r\n\tfi4 TEXT,\r\nCONSTRAINT PK_fi1 PRIMARY KEY (\r\n\ttranslation_memory_id, translation_unit_id\r\n)\r\n);')
            cursor.execute(
                'INSERT INTO fuzzy_data(translation_memory_id, translation_unit_id, fi1, fi2, fi4)\r\nSELECT x1.translation_memory_id, x1.translation_unit_id, x1.feature fi1, x2.feature fi2, x4.feature fi4\r\nFROM fuzzy_index1 x1\r\n\tINNER JOIN fuzzy_index2 x2 ON (x1.translation_memory_id = x2.translation_memory_id AND \r\n\t\t\t\t   x1.translation_unit_id = x2.translation_unit_id) \r\n\tINNER JOIN fuzzy_index4 x4 ON (x2.translation_memory_id = x4.translation_memory_id AND \r\n\t\t\t\t   x2.translation_unit_id = x4.translation_unit_id)\r\n')
            cursor.execute('DROP TABLE fuzzy_index1')
            cursor.execute('DROP TABLE fuzzy_index2')
            cursor.execute('DROP TABLE fuzzy_index4')

            self._setParameter(cursor, 'VERSION', '8.04')
            text = '8.04'
            flag = True
            cursor.execute('VACUUM')

        if text == '8.04':
            cursor.execute('ALTER TABLE fuzzy_data ADD COLUMN fi8 TEXT')
            self._setParameter(cursor, 'VERSION', '8.05')
            text = '8.05'
            flag = True

        if text == '8.05':
            cursor.execute('ALTER TABLE translation_memories ADD COLUMN flags INT NOT NULL DEFAULT 0')
            cursor.execute('ALTER TABLE translation_memories ADD COLUMN tucount INT NOT NULL DEFAULT 0')
            self._updateTuCounts()
            self._setParameter(cursor, 'VERSION', '8.06')
            flag = True

        if flag == False:
            raise ('ErrorCode.StorageVersionDataOutdated')

    def __get_tms(self, cursor, query):
        list = []
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            #start here
        return list
    def _getTms(self, cursor):
        self._checkVersion(cursor)

    def _importSdltmFile(self):
        try:
            conn = sqlite3.connect(self.FilePath)
            cursor = conn.cursor()





        except sqlite3.Error as e:
            print(f"Error reading SDLTM file: {e}")
            return []
        finally:
            if conn:
                conn.close()