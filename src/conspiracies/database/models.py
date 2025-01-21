from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship, Session, Mapped
from tqdm import tqdm

from conspiracies.corpusprocessing.clustering import Mappings

Base = declarative_base()


class EntityOrm(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String, nullable=False, index=True)
    supernode_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)
    is_supernode = Column(Boolean, nullable=False, default=False)
    term_frequency = Column(Integer, default=-1, nullable=False)
    doc_frequency = Column(Integer, default=-1, nullable=False)
    first_occurrence = Column(DateTime, nullable=True)
    last_occurrence = Column(DateTime, nullable=True)

    # Relationships
    supernode = relationship(
        "EntityOrm",
        back_populates="subnodes",
        remote_side="EntityOrm.id",
        foreign_keys="EntityOrm.supernode_id",
    )
    subnodes = relationship("EntityOrm", back_populates="supernode")

    subject_triplets: Mapped[list["TripletOrm"]] = relationship(
        "TripletOrm",
        back_populates="subject",
        foreign_keys="TripletOrm.subject_id",
    )
    object_triplets: Mapped[list["TripletOrm"]] = relationship(
        "TripletOrm",
        back_populates="object",
        foreign_keys="TripletOrm.object_id",
    )


class RelationOrm(Base):
    __tablename__ = "relations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String, nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)
    object_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)
    term_frequency = Column(Integer, default=-1, nullable=False)
    doc_frequency = Column(Integer, default=-1, nullable=False)
    first_occurrence = Column(DateTime, nullable=True)
    last_occurrence = Column(DateTime, nullable=True)

    # Relationships
    subject = relationship(
        "EntityOrm",
        foreign_keys="RelationOrm.subject_id",
    )
    object = relationship(
        "EntityOrm",
        foreign_keys="RelationOrm.object_id",
    )
    triplets: Mapped[list["TripletOrm"]] = relationship(
        "TripletOrm",
        back_populates="predicate",
        foreign_keys="TripletOrm.relation_id",
    )


class TripletOrm(Base):
    __tablename__ = "triplets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=True)
    doc_id = Column(Integer, ForeignKey("docs.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)
    relation_id = Column(Integer, ForeignKey("relations.id"), nullable=True, index=True)
    object_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)
    subj_span_start = Column(Integer, nullable=False)
    subj_span_end = Column(Integer, nullable=False)
    subj_span_text = Column(String, nullable=False)
    pred_span_start = Column(Integer, nullable=False)
    pred_span_end = Column(Integer, nullable=False)
    pred_span_text = Column(String, nullable=False)
    obj_span_start = Column(Integer, nullable=False)
    obj_span_end = Column(Integer, nullable=False)
    obj_span_text = Column(String, nullable=False)

    # Relationships
    subject = relationship(
        "EntityOrm",
        foreign_keys="TripletOrm.subject_id",
    )
    predicate = relationship(
        "RelationOrm",
        foreign_keys="TripletOrm.relation_id",
    )
    object = relationship(
        "EntityOrm",
        foreign_keys="TripletOrm.object_id",
    )
    document = relationship(
        "DocumentOrm",
        foreign_keys="TripletOrm.doc_id",
        back_populates="triplets",
    )

    # TODO: this should be here, but sometimes we see duplicates. Why?
    # __table_args__ = (UniqueConstraint(
    #     'doc_id',
    #     'subject_entity_id',
    #     'predicate_relation_id',
    #     'object_entity_id',
    #     name='unique_triplet_constraint'
    # ),)


class DocumentOrm(Base):
    __tablename__ = "docs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    orig_text = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=True)

    # Relationships
    triplets = relationship("TripletOrm", back_populates="document")


class EntityAndRelationCache:

    def __init__(self, session: Session, mappings: Mappings):
        self._session = session
        self._entities = {e.label: e for e in session.query(EntityOrm).all()}
        self._relations = {
            (int(r.subject_id), str(r.label), int(r.object_id)): r  # noqa
            for r in session.query(RelationOrm).all()
        }

        self._mappings = mappings

    def get_or_create_entity(self, label):
        """Fetch an entity by label, or create it if it doesn't exist."""
        mapped_entity = self._mappings.map_entity(label)

        entity = self._entities.get(mapped_entity, None)
        if entity is None:
            entity = EntityOrm(label=mapped_entity)
            self._session.add(entity)
            self._session.flush()  # Get the ID immediately
            self._entities[mapped_entity] = entity  # noqa
        return entity.id

    def get_or_create_relation(
        self,
        subject_id: int,
        object_id: int,
        predicate_label: str,
    ):
        """Fetch a relation by label, or create it if it doesn't exist."""
        mapped_predicate = self._mappings.map_predicate(predicate_label)
        relation_key = (
            subject_id,
            mapped_predicate,
            object_id,
        )

        relation = self._relations.get(relation_key, None)
        if relation is None:
            relation = RelationOrm(
                label=mapped_predicate,
                subject_id=subject_id,
                object_id=object_id,
            )
            self._session.add(relation)
            self._session.flush()  # Get the ID immediately
            self._relations[relation_key] = relation  # noqa
        return relation.id

    def update_entity_info(self, session: Session):
        for entity in tqdm(self._entities.values(), desc="Updating entity info"):
            as_subject = len(entity.subject_triplets)  # noqa
            as_object = len(entity.object_triplets)  # noqa
            entity.term_frequency = as_subject + as_object
            entity.doc_frequency = len(
                set(t.doc_id for t in entity.subject_triplets + entity.object_triplets),
            )
            dates = [
                t.timestamp for t in entity.subject_triplets + entity.object_triplets
            ]
            entity.first_occurrence = min(dates)
            entity.last_occurrence = max(dates)
            super_entity = self._mappings.get_super_entity(entity.label)
            if super_entity is not None:
                entity.supernode_id = self.get_or_create_entity(super_entity)
                entity.is_supernode = entity.id == entity.supernode_id
        session.commit()

    def update_relation_info(self, session: Session):
        for relation in tqdm(
            self._relations.values(),
            desc="Updating relation info",
        ):
            relation.term_frequency = len(relation.triplets)  # noqa
            relation.doc_frequency = len(set(t.doc_id for t in relation.triplets))
            dates = [t.timestamp for t in relation.triplets]
            relation.first_occurrence = min(dates)
            relation.last_occurrence = max(dates)
        session.commit()
