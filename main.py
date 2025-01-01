import argparse
from translate.storage import tmx
from translate.storage.base import TranslationStore
from fuzzy_searcher import FuzzySearcher
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo script for default arguments.")
    parser.add_argument("--tmpath", type=str, default="test/test.sdltm", help="First argument")
    parser.add_argument("--query", type=str, default="7/24/2022", help="Second argument")
    parser.add_argument("--maxResults", type=int, default=5, help="Second argument")
    parser.add_argument("--minScore", type=int, default=70, help="Second argument")
    args = parser.parse_args()
    main(args)