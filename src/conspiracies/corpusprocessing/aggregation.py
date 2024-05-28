from collections import Counter, defaultdict
from datetime import datetime
from typing import (
    List,
    TypedDict,
    Dict,
    Union,
    Callable,
    Iterable,
    Tuple,
    Optional,
    Any,
    Mapping,
)

from pydantic import BaseModel

from conspiracies.corpusprocessing.clustering import Mappings
from conspiracies.corpusprocessing.triplet import Triplet, TripletField


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
    docs: Optional[list[str]]
    first_occurrence: Optional[datetime]
    last_occurrence: Optional[datetime]
    alt_labels: Optional[list[str]]


class StatsDict(Dict[str, StatsEntry]):
    pass

    @classmethod
    def from_iterable(
        cls,
        generator: Iterable[Tuple[Any, Optional[str], Optional[datetime]]],
        alt_labels: Mapping[str, list[str]] = None,
    ):
        counter = Counter()
        docs = defaultdict(set)
        first_occurrence = {}
        last_occurrence = {}
        for key, doc_id, timestamp in generator:
            counter[key] += 1

            if doc_id:
                docs[key].add(doc_id)

            if timestamp:
                if key in first_occurrence:
                    first_occurrence[key] = min(timestamp, first_occurrence[key])
                else:
                    first_occurrence[key] = timestamp

                if key in last_occurrence:
                    last_occurrence[key] = max(timestamp, last_occurrence[key])
                else:
                    last_occurrence[key] = timestamp

        normalizer = min_max_normalizer(counter.values())

        return cls(
            {
                key: StatsEntry(
                    key=key,
                    frequency=value,
                    norm_frequency=normalizer(value),
                    docs=list(docs[key]) if key in docs else None,
                    first_occurrence=(
                        first_occurrence[key].isoformat()
                        if key in first_occurrence
                        else None
                    ),
                    last_occurrence=(
                        last_occurrence[key].isoformat()
                        if key in last_occurrence
                        else None
                    ),
                    alt_labels=(
                        alt_labels[key] if alt_labels and key in alt_labels else None
                    ),
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
        if self._mappings is not None:
            triplets = [
                Triplet(
                    subject=TripletField(
                        text=self._mappings.map_entity(t.subject.text),
                    ),
                    predicate=TripletField(
                        text=self._mappings.map_predicate(t.predicate.text),
                    ),
                    object=TripletField(text=self._mappings.map_entity(t.object.text)),
                    doc=t.doc,
                    timestamp=t.timestamp,
                )
                for t in triplets
            ]

        if remove_identical_subj_and_obj:
            triplets = [t for t in triplets if t.subject.text != t.object.text]

        return TripletStats(
            triplets=StatsDict.from_iterable(
                (
                    (
                        (t.subject.text, t.predicate.text, t.object.text),
                        t.doc,
                        t.timestamp,
                    )
                    for t in triplets
                )
            ),
            entities=StatsDict.from_iterable(
                (
                    (entity, t.doc, t.timestamp)
                    for t in triplets
                    for entity in [t.subject.text, t.object.text]
                ),
                self._mappings.entity_alt_labels(),
            ),
            predicates=StatsDict.from_iterable(
                ((t.predicate.text, t.doc, t.timestamp) for t in triplets),
                self._mappings.predicate_alt_labels(),
            ),
        )
