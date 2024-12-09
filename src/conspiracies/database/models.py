from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime,
)
from sqlalchemy.orm import declarative_base, relationship

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


class TripletOrm(Base):
    __tablename__ = "triplets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("docs.id"), nullable=False)
    subject_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    predicate_relation_id = Column(Integer, ForeignKey("relations.id"), nullable=False)
    object_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    subj_span_start = Column(Integer, nullable=True)
    subj_span_end = Column(Integer, nullable=True)
    pred_span_start = Column(Integer, nullable=True)
    pred_span_end = Column(Integer, nullable=True)
    obj_span_start = Column(Integer, nullable=True)
    obj_span_end = Column(Integer, nullable=True)

    # Relationships
    subject_entity = relationship(
        "EntityOrm",
        foreign_keys="TripletOrm.subject_entity_id",
    )
    predicate_relation = relationship(
        "RelationOrm",
        foreign_keys="TripletOrm.predicate_relation_id",
    )
    object_entity = relationship(
        "EntityOrm",
        foreign_keys="TripletOrm.object_entity_id",
    )
    document = relationship("DocumentOrm", back_populates="triplets")

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


def get_or_create_entity(label, session):
    """Fetch an entity by label, or create it if it doesn't exist."""
    entity = session.query(EntityOrm).filter_by(label=label).first()
    if not entity:
        entity = EntityOrm(label=label)
        session.add(entity)
        session.flush()  # Get the ID immediately
    return entity.id


def get_or_create_relation(label, session):
    """Fetch a relation by label, or create it if it doesn't exist."""
    relation = session.query(RelationOrm).filter_by(label=label).first()
    if not relation:
        relation = RelationOrm(label=label)
        session.add(relation)
        session.flush()  # Get the ID immediately
    return relation.id
