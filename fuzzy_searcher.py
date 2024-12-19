from difflib import SequenceMatcher

class Hit:
    def __init__(self, item, score):
        """
        Represents a single search result (hit).

        :param item: The matched item from the dataset.
        :param score: The similarity score of the match.
        """
        self.item = item
        self.score = score

    def __repr__(self):
        """String representation of a Hit object."""
        return f"Hit(item={self.item}, score={self.score:.2f})"

class FuzzySearcher:
    def __init__(self, dataset, max_results=5, min_score=0.5, scoring_method="Query"):
        """
        Initialize the FuzzySearcher.

        :param dataset: List of strings to search within.
        :param max_results: Maximum number of results to return.
        :param min_score: Minimum similarity score to consider a match.
        :param scoring_method: Scoring method to use ("Query", "Result", or "Dice").
        """
        self.dataset = dataset
        self.max_results = max_results
        self.min_score = min_score
        self.scoring_method = scoring_method
        self.last_key = None

    def _similarity(self, a, b):
        """
        Compute similarity between two strings using the selected scoring method.

        :param a: First string (query).
        :param b: Second string (dataset item).
        :return: Similarity score (float between 0 and 1).
        """
        if self.scoring_method == "Query":
            # Query-based similarity
            return SequenceMatcher(None, a, b).ratio()
        elif self.scoring_method == "Result":
            # Result-based similarity
            return SequenceMatcher(None, b, a).ratio()
        elif self.scoring_method == "Dice":
            # Dice coefficient-based similarity
            a_set, b_set = set(a), set(b)
            intersection = len(a_set & b_set)
            return 2 * intersection / (len(a_set) + len(b_set))
        else:
            raise ValueError("Invalid scoring method. Choose 'Query', 'Result', or 'Dice'.")

    def search(self, query):
        """
        Perform a fuzzy search for the given query.

        :param query: The search string.
        :return: A list of Hit objects representing matches.
        """
        results = []
        for item in self.dataset.units:
            score = self._similarity(query, item.source)
            if score >= self.min_score:
                results.append(Hit(item.source, score))

        # Sort results by score in descending order
        results.sort(key=lambda hit: hit.score, reverse=True)

        # Store the last query
        self.last_key = query

        # Return the top results
        return results[:self.max_results]
