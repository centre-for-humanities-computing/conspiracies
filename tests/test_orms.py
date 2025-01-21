import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from conspiracies.database.models import (
    Base,
    EntityOrm,
    RelationOrm,
    TripletOrm,
    DocumentOrm,
)


class TestModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up in-memory SQLite database
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        # Start a new session for each test
        self.session = self.Session()

    def tearDown(self):
        # Rollback changes after each test
        self.session.rollback()
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        # Dispose of the engine after all tests
        cls.engine.dispose()

    def test_triplet_relationships(self):
        # Create and commit entities
        subject = EntityOrm(label="Subject")
        obj = EntityOrm(label="Object")
        self.session.add_all([subject, obj])
        self.session.commit()

        # Create and commit relation and document
        relation = RelationOrm(label="Relates", subject_id=subject.id, object_id=obj.id)
        document = DocumentOrm(text="This is a document. Subject Relates Object.")
        self.session.add_all([relation, document])
        self.session.commit()

        # Create a triplet and link to entities, relation, and document
        triplet = TripletOrm(
            doc_id=document.id,
            subject_id=subject.id,
            object_id=obj.id,
            relation_id=relation.id,
            subj_span_text="Subject",
            subj_span_start=document.text.find("Subject"),
            subj_span_end=document.text.find("Subject") + 7,
            pred_span_text="Relates",
            pred_span_start=document.text.find("Relates"),
            pred_span_end=document.text.find("Relates") + 7,
            obj_span_text="Object",
            obj_span_start=document.text.find("Object"),
            obj_span_end=document.text.find("Object") + 6,
        )
        self.session.add(triplet)
        self.session.commit()

        # Verify forward relationships in TripletOrm
        self.assertEqual(triplet.subject, subject)
        self.assertEqual(triplet.object, obj)
        self.assertEqual(triplet.predicate, relation)
        self.assertEqual(triplet.document, document)

        # Verify reverse relationships in EntityOrm and RelationOrm
        self.assertIn(triplet, subject.subject_triplets)
        self.assertIn(triplet, obj.object_triplets)
        self.assertIn(triplet, relation.triplets)
        self.assertIn(triplet, document.triplets)

    def test_entity_supernode_subnodes(self):
        # Create and commit entities with supernode-subnode relationship
        parent = EntityOrm(label="Parent")
        self.session.add(parent)
        self.session.commit()
        child1 = EntityOrm(label="Child1", supernode_id=parent.id)
        child2 = EntityOrm(label="Child2", supernode_id=parent.id)
        self.session.add_all([child1, child2])
        self.session.commit()

        # Verify supernode-subnode relationships
        self.assertEqual(len(parent.subnodes), 2)
        self.assertIn(child1, parent.subnodes)
        self.assertIn(child2, parent.subnodes)
        self.assertEqual(child1.supernode, parent)
        self.assertEqual(child2.supernode, parent)

    # def test_unique_triplets(self):
    #     # Create and commit entities, relation, and document
    #     subject = EntityOrm(label="Subject")
    #     obj = EntityOrm(label="Object")
    #     relation = RelationOrm(label="Relates")
    #     document = DocumentOrm(text="This is a document.")
    #     self.session.add_all([subject, obj, relation, document])
    #     self.session.commit()
    #
    #     # Insert a triplet
    #     triplet1 = TripletOrm(
    #         doc_id=document.id,
    #         subject_id=subject.id,
    #         object_id=obj.id,
    #         relation_id=relation.id,
    #     )
    #     self.session.add(triplet1)
    #     self.session.commit()
    #
    #     # Try to insert a duplicate triplet
    #     triplet2 = TripletOrm(
    #         doc_id=document.id,
    #         subject_id=subject.id,
    #         object_id=obj.id,
    #         relation_id=relation.id,
    #     )
    #     self.session.add(triplet2)
    #
    #     # Ensure duplicate triplet raises an integrity error
    #     with self.assertRaises(Exception):
    #         self.session.commit()


if __name__ == "__main__":
    unittest.main()
