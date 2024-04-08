from collections import Counter
from typing import List, TypedDict, Dict, Union, Callable, Iterable, Tuple

from pydantic import BaseModel

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
    key: Union[str, Tuple[str]]
    frequency: int
    norm_frequency: float


class StatsDict(Dict[str, StatsEntry]):
    pass

    @classmethod
    def from_counter(cls, counter: Counter):
        normalizer = min_max_normalizer(counter.values())
        return cls(
            {
                key: StatsEntry(
                    key=key,
                    frequency=value,
                    norm_frequency=normalizer(value),
                )
                for key, value in counter.items()
            },
        )


class TripletStats(BaseModel):
    triplets: StatsDict
    entities: StatsDict
    predicates: StatsDict

    def entries(self) -> Dict[str, List[StatsEntry]]:
        return {
            statsdict: list(getattr(self, statsdict).values())
            for statsdict in ("triplets", "entities", "predicates")
        }


class TripletAggregator:

    def __init__(self, mappings: Mappings = None):
        self._mappings = mappings

    def aggregate(
        self,
        triplets: List[Triplet],
        remove_identical_subj_and_obj: bool = True,
    ):
        mapped_triplets = [
            (
                self._mappings.map_entity(triplet.subject.text),
                self._mappings.map_predicate(triplet.predicate.text),
                self._mappings.map_entity(triplet.object.text),
            )
            for triplet in triplets
        ]
        if remove_identical_subj_and_obj:
            mapped_triplets = [t for t in mapped_triplets if t[0] != t[2]]
        triplet_counts = Counter(triplet for triplet in mapped_triplets)
        entity_counts = Counter(
            entity for triplet in mapped_triplets for entity in (triplet[0], triplet[2])
        )
        predicate_counts = Counter(triplet[1] for triplet in mapped_triplets)
        return TripletStats(
            triplets=StatsDict.from_counter(triplet_counts),
            entities=StatsDict.from_counter(entity_counts),
            predicates=StatsDict.from_counter(predicate_counts),
        )
