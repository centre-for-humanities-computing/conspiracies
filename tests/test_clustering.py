from conspiracies.corpusprocessing.clustering import Clustering


class TestCombineClusters:
    def test_some_overlapping(self):
        clusters = [["a", "b"], ["b", "c"], ["d"]]
        expected = [["a", "b", "b", "c"], ["d"]]
        assert Clustering._combine_clusters(clusters) == expected

    def test_all_overlapping(self):
        clusters = [["a"], ["a"], ["a"]]
        expected = [["a", "a", "a"]]
        assert Clustering._combine_clusters(clusters) == expected

    def test_disjoint(self):
        clusters = [["a"], ["b"], ["c"]]
        expected = clusters
        assert Clustering._combine_clusters(clusters) == expected

    def test_empty_clusters(self):
        clusters = [[], ["a"], []]
        expected = clusters
        assert Clustering._combine_clusters(clusters) == expected

    def test_tuples_with_second_element_as_combine_key(self):
        clusters = [[("a", 1)], [("b", 2), ("c", 3)], [("a", 3), ("d", 4)]]
        expected = [[("a", 1)], [("b", 2), ("c", 3), ("a", 3), ("d", 4)]]
        assert (
            Clustering._combine_clusters(clusters, get_combine_key=lambda x: x[1])
            == expected
        )
