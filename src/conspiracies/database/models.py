from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime,
)
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()


class EntityOrm(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String, nullable=False, index=True)
    supernode_id = Column(Integer, ForeignKey("entities.id"), nullable=True)

    # Relationships
    supernode = relationship(
        "EntityOrm",
        back_populates="subnodes",
        remote_side="EntityOrm.id",
        foreign_keys="EntityOrm.supernode_id",
    )
    subnodes = relationship("EntityOrm", back_populates="supernode")


class RelationOrm(Base):
    __tablename__ = "relations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String, nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("entities.id"), nullable=True)
    object_id = Column(Integer, ForeignKey("entities.id"), nullable=True)

    subject = relationship(
        "EntityOrm",
        foreign_keys="RelationOrm.subject_id",
    )
    object = relationship(
        "EntityOrm",
        foreign_keys="RelationOrm.object_id",
    )


class TripletOrm(Base):
    __tablename__ = "triplets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("docs.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    relation_id = Column(Integer, ForeignKey("relations.id"), nullable=False)
    object_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    subj_span_start = Column(Integer, nullable=True)
    subj_span_end = Column(Integer, nullable=True)
    pred_span_start = Column(Integer, nullable=True)
    pred_span_end = Column(Integer, nullable=True)
    obj_span_start = Column(Integer, nullable=True)
    obj_span_end = Column(Integer, nullable=True)

    # Relationships
    subject_entity = relationship(
        "EntityOrm",
        foreign_keys="TripletOrm.subject_id",
    )
    predicate_relation = relationship(
        "RelationOrm",
        foreign_keys="TripletOrm.relation_id",
    )
    object_entity = relationship(
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
    timestamp = Column(DateTime)

    # Relationships
    triplets = relationship("TripletOrm", back_populates="document")


class ModelLookupCache:

    def __init__(self, session: Session):
        self._entities = {e.label: e for e in session.query(EntityOrm).all()}
        self._relations = {
            (int(r.subject_id), str(r.label), int(r.object_id)): r  # noqa
            for r in session.query(RelationOrm).all()
        }

    def get_or_create_entity(self, label, session):
        """Fetch an entity by label, or create it if it doesn't exist."""
        entity = self._entities.get(label, None)
        if entity is None:
            entity = EntityOrm(label=label)
            session.add(entity)
            session.flush()  # Get the ID immediately
            self._entities[label] = entity  # noqa
        return entity.id

    def get_or_create_relation(
        self,
        subject_id: int,
        object_id: int,
        label: str,
        session: Session,
    ):
        """Fetch a relation by label, or create it if it doesn't exist."""
        relation = self._relations.get((subject_id, label, object_id), None)
        if relation is None:
            relation = RelationOrm(
                label=label,
                subject_id=subject_id,
                object_id=object_id,
            )
            session.add(relation)
            session.flush()  # Get the ID immediately
            self._relations[(subject_id, label, object_id)] = relation  # noqa
        return relation.id
