from collections import Counter
from typing import List, TypedDict, Dict, Union, Callable, Iterable

from conspiracies.corpusprocessing.clustering import Mappings
from conspiracies.corpusprocessing.triplet import Triplet


def min_max_normalizer(values: Iterable[Union[int, float]]) -> Callable[[float], float]:
    if not isinstance(values, list):
        values = list(values)
    min_value = min(values)
    max_value = max(values)
    if min_value == max_value:
        return lambda x: 0
    return lambda x: (x - min_value) / (max_value - min_value)


class StatsEntry(TypedDict):
    frequency: int
    norm_frequency: float


class StatsDict(Dict[str, StatsEntry]):
    pass

    @classmethod
    def from_counter(cls, counter: Counter):
        normalizer = min_max_normalizer(counter.values())
        return cls(
            {
                key: StatsEntry(frequency=value, norm_frequency=normalizer(value))
                for key, value in counter.items()
            },
        )


class TripletStats(TypedDict):
    triplets: StatsDict
    entities: StatsDict
    predicates: StatsDict


class TripletAggregator:

    def __init__(self, mappings: Mappings = None):
        self._mappings = mappings

    def aggregate(self, triplets: List[Triplet]):
        mapped_triplets = [
            (
                self._mappings.map_entity(triplet.subject.text),
                self._mappings.map_predicate(triplet.predicate.text),
                self._mappings.map_entity(triplet.object.text),
            )
            for triplet in triplets
        ]
        triplet_counts = Counter(str(triplet) for triplet in mapped_triplets)
        entity_counts = Counter(
            entity for triplet in mapped_triplets for entity in (triplet[0], triplet[2])
        )
        predicate_counts = Counter(triplet[1] for triplet in mapped_triplets)
        return TripletStats(
            triplets=StatsDict.from_counter(triplet_counts),
            entities=StatsDict.from_counter(entity_counts),
            predicates=StatsDict.from_counter(predicate_counts),
        )
