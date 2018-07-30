from neomodel import StructuredNode, StringProperty, RelationshipTo, RelationshipFrom, config, db

config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'

class Association(StructuredNode):
    subject_prefix = StringProperty()
    subject_type = StringProperty()
    object_prefix = StringProperty()
    object_type = StringProperty()
    predicate = StringProperty()
    endpoint = StringProperty()

    def concept_assocations(prefix):
        params = {
            'subject_prefix' : prefix,
            'object_prefix' : prefix
        }

        results, meta = db.cypher_query(
            """
            MATCH (a:Association)
            WHERE
                TOLOWER(a.subject_prefix) = TOLOWER({subject_prefix}) AND
                (a.predicate = 'EquivalentAssociation' OR
                a.predicate = 'HasDescriptionAssociation')
            RETURN a
            """,
            params
        )

        return [Association.inflate(row[0]) for row in results]

    def statement_assocations(subject_prefix):
        """
        EquivalentAssociation mappings just give you information about the
        identifier, they don't relate you to new identifiers. This type of
        mapping will be useful for the /concepts endpoint
        """
        params = {
            'subject_prefix' : subject_prefix
        }

        results, meta = db.cypher_query(
            """
            MATCH (a:Association)
            WHERE
                TOLOWER(a.subject_prefix) CONTAINS TOLOWER({subject_prefix}) AND
                a.predicate <> 'EquivalentAssociation' AND
                a.predicate <> 'HasDescriptionAssociation'
            RETURN a
            """,
            params
        )

        return [Association.inflate(row[0]) for row in results]
