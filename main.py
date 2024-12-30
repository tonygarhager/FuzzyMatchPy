import sys
import argparse
from translate.storage import tmx
from translate.search import match
from translate.storage.base import TranslationStore
from fuzzy_searcher import FuzzySearcher
from FileBasedTranslationMemory import FileBasedTranslationMemory
from TranslationUnit import TranslationUnit
from SearchSettings import SearchSettings
from FileBasedTMHelper import FileBasedTMHelper
import json
import sqlite3

def read_sdltm(file_path):
    """
    Reads the content of an SDLTM file using sqlite3.

    :param file_path: Path to the .sdltm file
    :return: List of translation units with source and target segments
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        # Query the translation units table
        query = """
        SELECT
            tu.id AS translation_unit_id,
            src.text AS source_text,
            tgt.text AS target_text
        FROM
            TranslationUnits tu
        LEFT JOIN
            LanguageResources src ON tu.source_language_id = src.language_id
        LEFT JOIN
            LanguageResources tgt ON tu.target_language_id = tgt.language_id;
        """
        cursor.execute(query)

        # Fetch and display the results
        results = []
        for row in cursor.fetchall():
            results.append({"Source": row[1], "Target": row[2]})

        return results

    except sqlite3.Error as e:
        print(f"Error reading SDLTM file: {e}")
        return []
    finally:
        if conn:
            conn.close()

class TradosHandler:
    def __init__(self, fn):
        self.fn = fn
        self.tm = TranslationStore()

        if self.fn.endswith('.tmx'):
            self.load_tmx()

        self.matcher = FuzzySearcher(self.tm, 5, 0.1)

    def load_tmx(self):
        """
        Loads a TMX file and returns a list of translation units (source, target).
        """
        with open(self.fn, 'rb') as file:
            tmx_data = tmx.tmxfile(file)
            for unit in tmx_data.units:
                self.tm.addunit(unit)

    def fuzzy_match(self, source_text, threshold=0.8):
        """
        Performs fuzzy matching on the source text against the translation memory.
        :param source_text: The source text to search for.
        :param threshold: The minimum similarity threshold (0 to 1).
        :return: List of translation units that match the source text based on fuzzy matching.
        """
        match_result = self.matcher.search(source_text)
        return match_result

def main(args):
    # Example Usage
    path = args.tmpath
    query = args.query

    helper = FileBasedTMHelper()
    results = helper.fuzzy_search(path, query, 5, 70)

    json_res = {}
    i = 1
    for result in results.results:
        title = 'result ' + str(i)
        data = {}
        data['Match'] = str(result.scoring_result.match)
        data['SourceTu'] = str(result.memory_translation_unit.src_segment)
        data['TargetTu'] = str(result.memory_translation_unit.trg_segment)
        json_res[title] = data
        i += 1

    print(str(json_res))

    file_path = "result.json"

    # Write data to JSON file
    with open(file_path, "w") as json_file:
        json.dump(json_res, json_file, indent=4)

    print('Saved to result.json')
        #ftm = FileBasedTranslationMemory(path)
    #tu = TranslationUnit(ftm.tm.languageDirection['srcLang'], ftm.tm.languageDirection['trgLang'])
    #search_setting = get_search_setting(False, 5, 70)
    #ftm.search_translation_unit(search_setting, tu)
    #trados_handler = TradosHandler(tmx_path)
    #match_result = trados_handler.fuzzy_match(source_segment)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo script for default arguments.")
    parser.add_argument("--tmpath", type=str, default="test/test.sdltm", help="First argument")
    parser.add_argument("--query", type=str, default="7/24/2022", help="Second argument")
    parser.add_argument("--maxResults", type=int, default=5, help="Second argument")
    parser.add_argument("--minScore", type=int, default=70, help="Second argument")
    args = parser.parse_args()
    main(args)