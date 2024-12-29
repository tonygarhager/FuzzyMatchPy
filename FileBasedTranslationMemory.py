import sqlite3
from datetime import datetime
from uuid import UUID

from AnnotatedSegment import AnnotatedSegment
from AnnotatedTranslationUnit import AnnotatedTranslationUnit
from StringUtils import StringUtils
from BooleanSettingsWrapper import BooleanSettingsWrapper
from TranslationMemory import *
from Resource import Resource
from DefaultFallbackRecognizer import DefaultFallbackRecognizer
from typing import List
from SearchSettings import *
from SearchResults import *
from LanguageResources import *
from AnnotatedTranslationMemory import AnnotatedTranslationMemory
from WordCounts import *
from FuzzySearcher import *
from StoTranslationUnit import *
from StoSegment import *
from sortedcontainers import SortedDict
from Field import *
from XML import XmlSegmentSerializer
from SegmentSerialize import *
from TokenSerialization import *
from PesistentObjectToken import *
from datetime import datetime
from AbstractScorer import *

class FileBasedTranslationMemory:
    def __init__(self, tmPath):
        self.fuzzy_index_caches = [InMemoryFuzzyIndex()] * 10
        self.tm:TranslationMemory = None
        self.field_declaration = FieldDefinitions()
        # Set file path
        self.FilePath = tmPath
        self._create_connection()
        if self.FilePath.endswith('.sdltm'):
            self._importSdltmFile()

        self._origins_to_normalize = [TranslationUnitOrigin.Unknown,
			TranslationUnitOrigin.ContextTM,
			TranslationUnitOrigin.AdaptiveMachineTranslation,
			TranslationUnitOrigin.AutomaticTranslation,
			TranslationUnitOrigin.MachineTranslation,
			TranslationUnitOrigin.Nmt]

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
    def get_annotated_translation_memory(self, _id) -> AnnotatedTranslationMemory:
        tm = {}
        tm['resources_write_count'] = self.get_resources_write_count()
        tm['language_resources'] = self.get_language_resources(_id, True)
        tm['tm'] = self.get_translation_memory(_id)
        annotated_tm = AnnotatedTranslationMemory(tm['language_resources'], tm['resources_write_count'], tm['tm'])
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

    # SqliteStorage::GetAlignmentDataColspec()
    def get_alignment_data_colspec(self):
        if (self._supports_alignment_data() == False):
            return ", null, null, null "
        return ", alignment_data, align_model_date, insert_date "

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

        if not self._serializesTokens:
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
    def __get_tms(self, query) -> List[TranslationMemory]:
        lst = []
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            booleanSettingsWrapper = BooleanSettingsWrapper(row[7])
            expirationDate = None
            if row[10] is not None:
                expirationDate = datetime.strptime(row[10], '%Y-%m-%d %H:%M:%S')
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
                datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S'),
                desc,
                str(row[6]),
                expirationDate,
                booleanSettingsWrapper.tokenizerFlags,
                booleanSettingsWrapper.wordCountFlags)
            translationMemory.fuzzy_indexes = int(row[11])

            translationMemory.last_recompute_date = None
            if row[12] is not None:
                translationMemory.last_recompute_date = datetime.strptime(row[12], '%Y-%m-%d %H:%M:%S')
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

    def _importSdltmFile(self) -> TranslationMemory:
        lst = self._get_tms()
        self.tm = lst[0]

    def get_segment_hash(self, s):
        pass#mod

    @staticmethod
    def set_search_parameters_static(settings:SearchSettings):
        flag = True
        descending_order = None
        max_tu_id = None
        last_change_date = None

        if settings.sort_spec is not None:
            # Check if all criteria directions are not ascending and field name is not "chd"
            flag = all(criterion.direction != SortDirection.Ascending or criterion.field_name != "chd" for criterion in
                       settings.sort_spec.criteria)

        descending_order = flag
        max_tu_id = float('inf') if descending_order else -1

        # Set the date accordingly
        last_change_date = datetime.max if descending_order else datetime(1800, 1, 1)

        return max_tu_id, descending_order, last_change_date

    def set_search_parameters(self):
        return FileBasedTranslationMemory.set_search_parameters_static(self.settings)

    def search_translation_unit(self, settings:SearchSettings, tu: TranslationUnit):
        self.settings = settings
        anno_tm = self.get_annotated_translation_memory(self.tm.id)
        self.anno_tm = anno_tm
        if self.settings.mode == SearchMode.ConcordanceSearch or self.settings.mode == SearchMode.TargetConcordanceSearch:
            self._default_sort_order = SortSpecification(SearchResults.default_sort_order_concordance)
            self._scorer = Scorer(self.anno_tm, self.settings, True)
        else:
            self._default_sort_order = SortSpecification(SearchResults.default_sort_order)
            flag = self.settings.find_penalty(PenaltyType.CharacterWidthDifference) != None
            self._scorer = Scorer(self.anno_tm, self.settings, flag)

        anno_tu = AnnotatedTranslationUnit(anno_tm, tu, False, True)
        self.anno_tu = anno_tu
        is_concordance_search = settings.is_concordance_search
        flag = settings.mode == SearchMode.TargetConcordanceSearch

        if settings.min_score < SearchSettings.min_score_lower_bound:
            settings.min_score = SearchSettings.min_score_lower_bound

        if settings.max_results < 1:
            settings.max_results = 1

        search_results = SearchResults(settings.sort_spec)

        if flag:
            anno_tm.target_tools.ensure_tokenized_segment(tu.trg_segment)
        else:
            search_results.source_segment = tu.src_segment
            allow_token_bundles = is_concordance_search == False and tu.trg_segment is not None
            anno_tm.source_tools.ensure_tokenized_segment(tu.src_segment, False, allow_token_bundles)

            if tu.trg_segment is not None:
                anno_tm.target_tools.ensure_tokenized_segment(tu.trg_segment, False, allow_token_bundles)
                search_results.document_placeable = PlaceableComputer.compute_placeables(tu.src_segment, tu.trg_segment)
            elif is_concordance_search == False:
                search_results.document_placeable = PlaceableComputer.compute_placeables(tu.src_segment, None)
            #mod search_results.source_hash = self.get_segment_hash(tu.src_segment)
            word_count_options = WordCountsOptions()
            word_count_options.break_on_tag = (anno_tm.tm.word_count_flags & WordCountFlags.BreakOnTag) == WordCountFlags.BreakOnTag
            word_count_options.break_on_hyphen = (anno_tm.tm.word_count_flags & WordCountFlags.BreakOnHyphen) == WordCountFlags.BreakOnHyphen
            word_count_options.break_on_dash = (anno_tm.tm.word_count_flags & WordCountFlags.BreakOnDash) == WordCountFlags.BreakOnDash
            word_count_options.break_on_apostrophe = (anno_tm.tm.word_count_flags & WordCountFlags.BreakOnApostrophe) == WordCountFlags.BreakOnApostrophe
            word_count_options.break_advanced_tokens_by_character = settings.advanced_tokenization_legacy_scoring
            search_results.source_word_counts = WordCounts(tu.src_segment.tokens, word_count_options, tu.src_segment.culture_name)

        last_tu_id, flag2, last_change_date = self.set_search_parameters()
        num = max(SearchSettings.min_score_lower_bound, self.settings.min_score - 20)
        num2 = self.settings.max_results
        if num2 < 20 and self.settings.mode != SearchMode.DuplicateSearch:
            num2 = 20
        num3 = max(50, num2)

        #mod unneed because Searcher._exactSearchTestPageSize is always -1
        list = []
        num4 = 0

        if (self.settings.mode == SearchMode.ExactSearch or
            self.settings.mode == SearchMode.NormalSearch or
            self.settings.mode == SearchMode.FullSearch or
            self.settings.mode == SearchMode.DuplicateSearch):
            pass#mod
        elif self.settings.mode == SearchMode.ConcordanceSearch:
            last_tu_id = self.run_concordance_search(anno_tu.source, True, num, num2, last_tu_id, search_results, flag2)
        elif self.settings.mode == SearchMode.TargetConcordanceSearch:
            last_tu_id = self.run_concordance_search(anno_tu.target, False, num, num2, last_tu_id, search_results, flag2)

        if search_results is None:
            return None

        search_results.results = [r for r in search_results.results if r.scoring_result.match >= self.settings.min_score]

        # Check if SortSpecification is not None and contains sort criteria
        if self.settings.sort_spec and len(self.settings.sort_spec) > 0 and len(search_results.results) > 1:
            # Perform sorting based on SortSpecification
            search_results.results.sort(key=self._get_sort_key(self.settings.sort_spec))
        else:
            # Perform default sorting
            search_results.results.sort(key=self._get_sort_key(self._DefaultSortOrder))

        # Cap the results at the maximum allowed number
        if len(search_results.results) > self.settings.max_results:
            search_results.results = search_results.results[:self.settings.max_results]

        return search_results

    def ensure_fuzzy_index_loaded(self, type:FuzzyIndexes):
        #if type in self.fuzzy_index_caches.keys():
        #    return
        self.fuzzy_index_caches[type]:InMemoryFuzzyIndex = InMemoryFuzzyIndex()
        sqlcmd = 'SELECT translation_memory_id, translation_unit_id, fi' + str(int(type)) + ' FROM fuzzy_data ORDER BY translation_unit_id ASC'
        self.cursor.execute(sqlcmd)
        rows = self.cursor.fetchall()
        for row in rows:
            nint = int(row[1])
            text = None if row[2] is None else str(row[2])
            list = []

            if text is not None:
                array = text.split('|')
                for i in range(len(array)):
                    item = int(array[i])
                    list.append(item)

            self.fuzzy_index_caches[type].add(nint, list)
    def serializes_tokens(self) -> bool:
        self._check_version()
        return self._serializesTokens

    def fuzzy_search(self, tm_id:int, feature:[], index:FuzzyIndexes, min_score:int, max_hits:int, concordance:bool, last_tuid:int,
                     tu_context_data:TuContextData, descending_order:bool)->[]:
        self.ensure_fuzzy_index_loaded(index)
        alignment_data_col_spec = self.get_alignment_data_colspec()
        scoring_method = ScoringMethod.QUERY if concordance else ScoringMethod.DICE
        list = self.fuzzy_index_caches[int(index)].search(feature, max_hits, min_score, last_tuid, scoring_method, None, descending_order)

        if list is None or len(list) == 0:
            return []
        query = 'SELECT id, guid, translation_memory_id, \r\n\t\t\t\tsource_hash, source_segment, 0, 0, \r\n\t\t\t\ttarget_hash, target_segment, 0, 0, \r\n\t\t\t\tcreation_date, creation_user, change_date, change_user, last_used_date, last_used_user, usage_counter, flags '
        if self.serializes_tokens():
            query += ', source_token_data, target_token_data '
        else:
            query += ', null, null '
        query += alignment_data_col_spec + ', 0, null, null FROM translation_units WHERE id IN ('
        flag = True
        for hit in list:
            if flag:
                flag = False
            else:
                query += ','
            query += str(hit.key)
        query += ')'
        param = {"@tm_id": tm_id}
        command = [query, param]

        tuset = self.get_tu_set(command, max_hits, tu_context_data)
        return tuset

    @property
    def has_flag(self):
        return True

    @property
    def has_guids(self):
        return True

    def read_tu_with_flags(self, row):
        field_count = len(row)

        def get_int(idx):
            return None if row[idx] is None else int(row[idx])

        def get_string(idx):
            return None if row[idx] is None else str(row[idx])

        def get_bytes(idx):
            return None if row[idx] is None else row[idx]

        def get_date(idx):
            return None if row[idx] is None else datetime.fromisoformat(row[idx])

        if field_count - 10 > 1:
            if field_count == 14:
                return StoTranslationUnit(
                    get_int(0),
                    get_string(1) if self.has_guids else get_string(1),
                    0,
                    StoSegment(get_int(2), 0, get_string(3), None, get_bytes(12)),
                    StoSegment(get_int(4), 0, get_string(5), None, get_bytes(13)),
                    datetime.utcnow(),  # Default date
                    "",
                    datetime.utcnow(),  # Default date
                    "",
                    datetime.utcnow(),  # Default date
                    "",
                    0,
                    0,
                    get_bytes(6),
                    get_bytes(7),
                    get_bytes(8),
                    get_date(9),
                    get_date(10),
                    get_int(11),
                )
            elif field_count == 23:
                return StoTranslationUnit(
                    get_int(0),
                    get_string(1) if self.has_guids else get_string(1),
                    get_int(2),
                    StoSegment(get_int(3), 0, get_string(4), None, get_bytes(21)),
                    StoSegment(get_int(5), 0, get_string(6), None, get_bytes(22)),
                    get_date(7),
                    get_string(8),
                    get_date(9),
                    get_string(10),
                    get_date(11),
                    get_string(12),
                    get_int(13),
                    get_int(14),
                    get_bytes(15),
                    get_bytes(16),
                    get_bytes(17),
                    get_date(18),
                    get_date(19),
                    get_int(20),
                )
            elif field_count == 25:
                return StoTranslationUnit(
                    get_int(0),
                    get_string(1) if self.has_guids else get_string(1),
                    get_int(2),
                    StoSegment(get_int(3), 0, get_string(4) or get_string(5), None, get_bytes(23)),
                    StoSegment(get_int(6), 0, get_string(7) or get_string(8), None, get_bytes(24)),
                    get_date(9),
                    get_string(10),
                    get_date(11),
                    get_string(12),
                    get_date(13),
                    get_string(14),
                    get_int(15),
                    get_int(16),
                    get_bytes(17),
                    get_bytes(18),
                    get_bytes(19),
                    get_date(20),
                    get_date(21),
                    get_int(22),
                )
            elif field_count == 27:
                return StoTranslationUnit(
                    get_int(0),
                    get_string(1) if self.has_guids else get_string(1),
                    get_int(2),
                    StoSegment(get_int(3), 0, get_string(4), None, get_bytes(25)),
                    StoSegment(get_int(7), 0, get_string(8), None, get_bytes(26)),
                    get_date(11),
                    get_string(12),
                    get_date(13),
                    get_string(14),
                    get_date(15),
                    get_string(16),
                    get_int(17),
                    get_int(18),
                    get_bytes(19),
                    get_bytes(20),
                    get_bytes(21),
                    get_date(22),
                    get_date(23),
                    get_int(24),
                )
            else:
                raise Exception("Invalid data retrieved from storage")
        else:
            return StoTranslationUnit(
                get_int(0),
                str(int=0),  # Default GUID
                0,
                StoSegment(get_int(1), 0, get_string(2), None, get_bytes(8)),
                StoSegment(0, 0, get_string(3), None, get_bytes(9)),
                datetime.utcnow(),  # Default date
                "",
                datetime.utcnow(),  # Default date
                "",
                datetime.utcnow(),  # Default date
                "",
                0,
                get_int(6),
                get_bytes(4),
                get_bytes(5),
                None,
                None,
                None,
                get_int(7),
            )

    def read_tu(self, row)->StoTranslationUnit:
        #mod if self.has_flag == False:
        #    return self.read_tu_no_flags(row)
        return self.read_tu_with_flags(row)

    def read_attribute_values(self, reader, tus, tu_index, auto_advance_result_set, attributes=None):
        if attributes is None:
            attributes = {}

        list_ = []
        list2 = []

        while True:
            obj = None
            num = 0
            num2 = 0
            name = None
            num3 = 0

            while reader.read():
                num4 = 0
                flag = reader.field_count == 5
                int_val = self.get_int32(reader, num4)
                num4 += 1
                int2 = self.get_int32(reader, num4)
                num4 += 1

                if flag:
                    text = reader.get_string(num4)
                    num4 += 1
                    num5 = self.get_int32(reader, num4)
                else:
                    if int2 not in attributes:
                        raise Exception("Invalid attribute ID")

                    attribute_declaration = attributes[int2]
                    text = attribute_declaration.name
                    num5 = int(attribute_declaration.type)

                if (int_val != num and num != 0) or (int2 != num2 and num2 != 0):
                    if num in tu_index:
                        translation_unit = tus[tu_index[num]]
                        if num3 != 2:
                            if num3 == 5:
                                translation_unit.attributes.append(
                                    AttributeValue(num2, name, FieldValueType(num3), list2))
                            else:
                                translation_unit.attributes.append(
                                    AttributeValue(num2, name, FieldValueType(num3), obj))
                        else:
                            list_.sort()
                            translation_unit.attributes.append(AttributeValue(num2, name, FieldValueType(num3), list_))

                    list2.clear()
                    list_.clear()

                if num5 == 2:
                    list_.append(reader.get_string(num4))
                elif num5 == 3:
                    obj = self.get_datetime(reader, num4)
                elif num5 == 4:
                    obj = reader.get_value(num4)
                    if isinstance(obj, (decimal, long)):
                        obj = self.get_int32(reader, num4)
                elif num5 == 5:
                    list2.append(self.get_int32(reader, num4))

                num4 += 1
                num2 = int2
                name = text
                num3 = num5
                num = int_val

            if num2 != 0:
                if num in tu_index:
                    translation_unit = tus[tu_index[num]]
                    if num3 != 2:
                        if num3 == 5:
                            translation_unit.attributes.append(AttributeValue(num2, name, FieldValueType(num3), list2))
                        else:
                            translation_unit.attributes.append(AttributeValue(num2, name, FieldValueType(num3), obj))
                    else:
                        list_.sort()
                        translation_unit.attributes.append(AttributeValue(num2, name, FieldValueType(num3), list_))

            if not auto_advance_result_set or not reader.next_result():
                return

    def get_tu_set(self, command, count: int, tu_context_data: TuContextData):
        list_of_tus = []
        dictionary = {}
        ids_string = []

        # Execute the initial search query
        self.cursor.execute(command[0], command[1])
        rows = self.cursor.fetchall()
        for row in rows:
            translation_unit = self.read_tu(row)  # Assuming read_tu is a function that processes the row into a TranslationUnit
            dictionary[translation_unit.id] = len(list_of_tus)

            if len(list_of_tus) > 0:
                ids_string.append(", ")
            ids_string.append(str(translation_unit.id))
            list_of_tus.append(translation_unit)

            if count > 0 and len(list_of_tus) >= count:
                break

        ids_str = "".join(ids_string)

        if not list_of_tus:
            return list_of_tus

        # Execute the second query to fetch attribute values
        query = f"""
            SELECT da.translation_unit_id, da.attribute_id, a.name, a.type, da.value
            FROM date_attributes da INNER JOIN attributes a ON da.attribute_id = a.id 
            WHERE da.translation_unit_id IN ({0}) 
            ORDER BY da.translation_unit_id, da.attribute_id;
            """
        query = query.replace('(0)', '(' + ids_str + ')')
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        query = f"""
            SELECT sa.translation_unit_id, sa.attribute_id, a.name, a.type, sa.value 
            FROM string_attributes sa INNER JOIN attributes a ON sa.attribute_id = a.id
            WHERE sa.translation_unit_id IN ({0}) 
            ORDER BY sa.translation_unit_id, sa.attribute_id;
            """
        query = query.replace('(0)', '(' + ids_str + ')')
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        query = f"""
            SELECT na.translation_unit_id, na.attribute_id, a.name, a.type, na.value 
            FROM numeric_attributes na INNER JOIN attributes a ON na.attribute_id = a.id
            WHERE na.translation_unit_id IN ({0}) 
            ORDER BY na.translation_unit_id, na.attribute_id;
            """
        query = query.replace('(0)', '(' + ids_str + ')')
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        query = f"""
            SELECT pa.translation_unit_id, pv.attribute_id, a.name, a.type, pa.picklist_value_id FROM picklist_attributes pa 
            INNER JOIN picklist_values pv ON pv.id = pa.picklist_value_id
            INNER JOIN attributes a ON pv.attribute_id = a.id
            WHERE pa.translation_unit_id IN ({0})
            ORDER BY pa.translation_unit_id, pv.attribute_id
            """
        query = query.replace('(0)', '(' + ids_str + ')')
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        #read_attribute_values(rows, list_of_tus, dictionary, True, None)  # Assuming read_attribute_values processes the rows

        # Process Text Context if available
        if tu_context_data.text_context and tu_context_data.text_context.context1 != -1:
            query = f"""
                SELECT translation_unit_id, left_source_context, left_target_context
                FROM translation_unit_contexts
                WHERE translation_unit_id IN ({ids_str})
                AND left_source_context={tu_context_data.text_context.context1}
                """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            read_text_contexts(rows, list_of_tus, dictionary)  # Assuming read_text_contexts processes the rows

        # Process ID Context if available
        if tu_context_data.id_context:
            query = f"""
                SELECT translation_unit_id, idcontext
                FROM translation_unit_idcontexts
                WHERE translation_unit_id IN ({ids_str})
                AND idcontext='{tu_context_data.id_context}'
                """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            read_id_contexts(rows, list_of_tus, dictionary)  # Assuming read_id_contexts processes the rows

        return list_of_tus

    def deserialize_tu_segments(self, storage_tu:StoTranslationUnit, tu:TranslationUnit, source_culture_name:str, target_culture_name:str):
        if storage_tu.serialization_version == 0:
            xml_segment_serializer = XmlSegmentSerializer()
            tu.src_segment = xml_segment_serializer.deserialize_segment(storage_tu.source.text)
            tu.trg_segment = xml_segment_serializer.deserialize_segment(storage_tu.target.text)
            return
        tu.src_segment = SegmentSerialization.load(storage_tu.source, source_culture_name)
        tu.trg_segment = SegmentSerialization.load(storage_tu.target, target_culture_name)

    def get_translation_unit(self, storage_tu:StoTranslationUnit, fields: FieldDefinitions, source_culture_name:str, target_culture_name:str):
        translation_unit = TranslationUnit()
        self.deserialize_tu_segments(storage_tu, translation_unit, source_culture_name, target_culture_name)
        translation_unit.src_segment.tokens = TokenSerialization.load_tokens(storage_tu.source_token_data, translation_unit.src_segment)
        translation_unit.trg_segment.tokens = TokenSerialization.load_tokens(storage_tu.target_token_data, translation_unit.trg_segment)
        self.fill_remaining_translation_unit_details(translation_unit, storage_tu, fields)
        translation_unit.resource_id = PersistentObjectToken(storage_tu.id, storage_tu.guid)
        return translation_unit

    @staticmethod
    def set_tu_flags_legacy_column(tu:TranslationUnit, storage_tu:StoTranslationUnit):
        num = storage_tu.flags
        try:
            num2 = num & 255
            tu.origin:TranslationUnitOrigin = num2
            num >>= 8
            num2 = num & 255
            tu.format:TranslationUnitFormat = num2
            num >>= 8
            num2 = num & 255
            tu.confirmationLevel:ConfirmationLevel = num2
        except Exception:
            pass

    def set_tu_flags(self, tu:TranslationUnit, storage_tu:StoTranslationUnit):
        FileBasedTranslationMemory.set_tu_flags_legacy_column(tu, storage_tu)

        if tu.origin in self._origins_to_normalize:
            tu.origin = TranslationUnitOrigin.TM


    def fill_remaining_translation_unit_details(self, tu:TranslationUnit, storage_tu:StoTranslationUnit, fields: FieldDefinitions):
        if storage_tu is None:
            raise Exception('storageTu')
        tu.origin = TranslationUnitOrigin.TM
        tu.system_fields.use_count = storage_tu.usage_counter
        tu.system_fields.use_date = storage_tu.last_used_date
        tu.system_fields.use_user = storage_tu.last_used_user
        tu.system_fields.creation_user = storage_tu.creation_user
        tu.system_fields.creation_date = storage_tu.creation_date
        tu.system_fields.change_user = storage_tu.change_user
        tu.system_fields.change_date = storage_tu.change_date
        tu.contexts = storage_tu.contexts
        tu.id_contexts = storage_tu.id_contexts
        tu.alignment_data = storage_tu.alignment_data
        tu.align_model_date = storage_tu.align_model_date
        tu.insert_date = storage_tu.insert_date
        tu.field_values = fields#mod
        self.set_tu_flags(tu, storage_tu)

        PlaceableComputer.convert_placeables_to_alignments(PlaceableComputer.compute_placeables(tu.src_segment, tu.trg_segment), tu.alignment_data, tu.src_segment.tokens, tu.trg_segment.tokens)


    def set_last_tuid(tu:StoTranslationUnit, last_tuid, last_change_date, order_descending, skip_rows):
        if tu.id > last_tuid and not order_descending:
            last_tuid = tu.id
        if tu.id < last_tuid and order_descending:
            last_tuid = tu.id
        if tu.change_date > last_change_date and not order_descending:
            last_change_date = tu.change_date
            skip_rows = 1
            return last_tuid, last_change_date, skip_rows
        if tu.change_date < last_change_date and order_descending:
            last_change_date = tu.change_date
            skip_rows = 1
            return last_tuid, last_change_date, skip_rows
        if tu.change_date == last_change_date:
            skip_rows += 1

        return last_tuid, last_change_date, skip_rows

    def add_tus_to_result(self, doc_src_segment:AnnotatedSegment, doc_trg_segment:AnnotatedSegment,
                          results:SearchResults, tus:List[StoTranslationUnit], used_index: FuzzyIndexes,
                          translator, tu_context_data: TuContextData, last_tuid: int, last_change_date: datetime,
                          order_descending:bool, acronym_token_indices:[int], skip_rows:int):
        id_context_matching_candidates_exhausted = False
        id_context_matching_candidates_found = False
        unmatched_acronyms = (acronym_token_indices is not None and len(acronym_token_indices) > 0)

        if tus is None or len(tus) == 0:
            id_context_matching_candidates_exhausted = True
            return 0, last_tuid, last_change_date, id_context_matching_candidates_found, id_context_matching_candidates_exhausted, unmatched_acronyms, skip_rows
        num = 0
        flag = False
        sorted_list = SortedDict()
        for i in range(len(results.results)):
            search_result = results.results[i]
            sorted_list[search_result.memory_translation_unit.id] = True

        for translation_unit in tus:
            last_tuid, last_change_date, skip_rows = FileBasedTranslationMemory.set_last_tuid(translation_unit, last_tuid, last_change_date, order_descending, skip_rows)
            if not translation_unit.id in sorted_list.keys():
                translation_unit2 = self.get_translation_unit(translation_unit, self.field_declaration, self.anno_tu.translation_unit.src_segment.culture_name, self.anno_tu.translation_unit.trg_segment.culture_name)
                search_result2 = SearchResult(translation_unit2)

                if self.settings.is_concordance_search == False:
                    self.anno_tm.source_tools.ensure_tokenized_segment(search_result2.memory_translation_unit.src_segment, False, True)
                    self.anno_tm.target_tools.ensure_tokenized_segment(search_result2.memory_translation_unit.trg_segment, False, True)
                if (self.settings.mode != SearchMode.DuplicateSearch or
                    (len(translation_unit2.src_segment.tokens) == len(doc_src_segment.segment.tokens) and
                    len(translation_unit2.trg_segment.tokens) == len(doc_trg_segment.segment.tokens))):
                    if self.settings.is_concordance_search == False:
                        search_result2.memory_placeables = PlaceableComputer.compute_placeables(translation_unit2)
                    if self.settings.is_document_search == False:
                        tu_context_data.text_context = None
                    search_result2.scoring_result = ScoringResult()
                    #mod
                    if search_result2.scoring_result.id_context_match == False:
                        id_context_matching_candidates_exhausted = True
                    else:
                        id_context_matching_candidates_exhausted = False

                    self._scorer.compute_scores(search_result2, doc_src_segment, doc_trg_segment, None, tu_context_data, self.settings.mode == SearchMode.DuplicateSearch, used_index, False)

                    if search_result2.scoring_result.match >= self.settings.min_score:
                        #mod
                        if search_result2.scoring_result.match >= self.settings.min_score and (self.settings.mode != SearchMode.ExactSearch or search_result2.scoring_result.is_exact_match):
                            search_result2.context_data = TuContext(translation_unit.source.hash, translation_unit.target.hash)
                            results.results.append(search_result2)
                            sorted_list[search_result2.memory_translation_unit.id] = True
                            num += 1
                            if search_result2.scoring_result.is_exact_match:
                                flag = True
        return num

    def run_concordance_search(self, segment:AnnotatedSegment, is_source:bool, adjusted_minscore:int, adjusted_maxresults:int,
                               max_tuid:int, results:SearchResults, descending_order:bool)->int:
        min_value = datetime.min
        if is_source:
            fuzzy_indexes = FuzzyIndexes.SourceCharacterBased
            fuzzy_indexes2 = FuzzyIndexes.SourceWordBased
        else:
            fuzzy_indexes = FuzzyIndexes.TargetCharacterBased
            fuzzy_indexes2 = FuzzyIndexes.TargetWordBased

        if (self.tm.fuzzy_indexes & fuzzy_indexes) == 0 and (self.tm.fuzzy_indexes & fuzzy_indexes2) == 0:
            raise Exception('ErrorCode.TMSearchModeNotSupported')

        list2 = []
        list = segment.tm_feature_vector
        if (self.tm.fuzzy_indexes & fuzzy_indexes2) != 0:
            if list and len(list) > 0:
                while True:
                    list2 = self.fuzzy_search(self.tm.id, list, fuzzy_indexes2,
                                                               adjusted_minscore, adjusted_maxresults, True, max_tuid,
                                                               TuContextData(), descending_order)
                    if list2 and len(list2) > 0:
                        num = 0
                        if is_source:
                            self.add_tus_to_result(segment, None, results, list2, fuzzy_indexes2, None, TuContextData(),
                                                max_tuid, min_value, descending_order, None, num)
                        else:
                            self.add_tus_to_result(None, segment, results, list2, fuzzy_indexes2, None, TuContextData(),
                                                max_tuid, min_value, descending_order, None, num)
                    if not (list2 and len(list2) == adjusted_maxresults and results.count() < adjusted_maxresults):
                        break

        if (self.tm.fuzzy_indexes & fuzzy_indexes) == 0:
            return max_tuid

        max_tu_id = 0
        list = segment.concordance_feature_vector
        if not list or len(list) <= 0:
            return max_tuid

        while True:
            list2 = self.fuzzy_search(self.tm.id, list, fuzzy_indexes, adjusted_minscore,
                                                       adjusted_maxresults, False, max_tuid, TuContextData(), False)
            if list2 and len(list2) > 0:
                num2 = 0
                if is_source:
                    self.add_tus_to_result(segment, None, results, list2, fuzzy_indexes, None, TuContextData(), max_tuid,
                                        min_value, False, None, num2)
                else:
                    self.add_tus_to_result(None, segment, results, list2, fuzzy_indexes, None, TuContextData(), max_tuid,
                                        min_value, False, None, num2)
            if not (list2 and len(list2) == adjusted_maxresults and results.count() < adjusted_maxresults):
                break
        return max_tuid






