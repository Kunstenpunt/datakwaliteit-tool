from PyQt6.QtCore import pyqtSignal, QObject

from .utils import strip_url_part


class Property:
    def __init__(self, identifier, label):
        self.identifier = identifier
        self.label = label
        self.constraints = []

    def __str__(self):
        return f"{self.label} ({self.identifier}): {[str(c) for c in self.constraints]}"


class Constraint(QObject):
    violationsUpdated = pyqtSignal()

    def __init__(self, identifier, label, prop):
        super().__init__()

        self.property = prop
        self.identifier = identifier
        self.label = label
        self.violations = None

    def __str__(self):
        return f"{self.label} ({self.identifier})"

    def pretty(self):
        return f'"{self.label}" ({self.identifier}) on "{self.property.label}" ({self.property.identifier})'

    def query_violations(self, wikibase_helper):
        print(f"Querying violations not implemented for {self}")


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Single_value
class SingleValueConstraint(Constraint):
    seperatorsUpdated = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.separators = []

    def _query_qualifiers(self, wikibase_helper):
        query = f"""
            SELECT DISTINCT ?pq_obj ?pq_objLabel
            WHERE
            {{
                ?statement kpps:P85 kp:Q1585537 .
                kp:{self.property.identifier} kpp:P85 ?statement .
                ?statement kppq:P90 ?pq_obj .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        result = wikibase_helper.execute_query(query)
        for [identifier, label] in result[1:]:
            self.separators.append(Property(strip_url_part(identifier), label))
        self.seperatorsUpdated.emit()

    def query_violations(self, wikibase_helper):
        self._query_qualifiers(wikibase_helper)
        query = f"""
            SELECT ?entity (COUNT(?value) AS ?valueCount)
            WHERE
            {{
                ?entity kpp:{self.property.identifier} ?statement .
                ?statement kpps:{self.property.identifier} ?value .
                {'\n'.join(f'MINUS {{ ?statement kppq:{s.identifier} ?seperator }} .' for s in self.separators)}             
            }}
            GROUP BY ?entity
            HAVING(?valueCount > 1)
        """
        result = wikibase_helper.execute_query(query)
        self.violations = [[strip_url_part(e), v] for [e, v] in result]
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Value_class
class ValueTypeConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes = []
        self.relation = None

    def _query_qualifiers(self, wikibase_helper):
        query = f"""
            SELECT DISTINCT ?class ?classLabel ?relation ?relationLabel
            WHERE
            {{
                ?statement kpps:P85 kp:Q1585538 .
                kp:{self.property.identifier} kpp:P85 ?statement .
                OPTIONAL {{ ?statement kppq:P86 ?class }}
                OPTIONAL {{ ?statement kppq:P87 ?relation }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        result = wikibase_helper.execute_query(query)
        for [class_id, class_label, relation_id, relation_label] in result[1:]:
            class_id = strip_url_part(class_id)
            relation_id = strip_url_part(relation_id)
            if relation_id != "Q1585615":
                print(
                    f'ValueTypeConstraint for relation "{relation_label}" is currently unsupported.'
                )
                self.relation = None
            self.classes.append(Property(class_id, class_label))
        self.relation = "P1"

    def query_violations(self, wikibase_helper):
        self._query_qualifiers(wikibase_helper)
        if self.relation != "P1":
            return
        query = f"""
            SELECT DISTINCT ?entity ?value
            WHERE
            {{
                ?entity kpt:{self.property.identifier} ?value .
                {'\n'.join(f'MINUS {{ ?value kpt:{self.relation} kp:{c.identifier}}} .' for c in self.classes)}
            }}
        """
        result = wikibase_helper.execute_query(query)
        self.violations = [[strip_url_part(e), strip_url_part(v)] for [e, v] in result]
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Subject_class
class SubjectTypeConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes = []
        self.relation = None

    def _query_qualifiers(self, wikibase_helper):
        query = f"""
            SELECT DISTINCT ?class ?classLabel ?relation ?relationLabel
            WHERE
            {{
                ?statement kpps:P85 kp:Q1585539 .
                kp:{self.property.identifier} kpp:P85 ?statement .
                OPTIONAL {{ ?statement kppq:P86 ?class }}
                OPTIONAL {{ ?statement kppq:P87 ?relation }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        result = wikibase_helper.execute_query(query)
        for [class_id, class_label, relation_id, relation_label] in result[1:]:
            class_id = strip_url_part(class_id)
            relation_id = strip_url_part(relation_id)
            if relation_id != "Q1585615":
                print(
                    f'SubjectTypeConstraint for relation "{relation_label}" is currently unsupported.'
                )
                self.relation = None
            self.classes.append(Property(class_id, class_label))
        self.relation = "P1"

    def query_violations(self, wikibase_helper):
        self._query_qualifiers(wikibase_helper)
        if self.relation != "P1":
            return
        query = f"""
            SELECT DISTINCT ?entity
            WHERE
            {{
                ?entity kpt:{self.property.identifier} ?value .
                {'\n'.join(f'MINUS {{ ?entity kpt:{self.relation} kp:{c.identifier}}} .' for c in self.classes)}
            }}
        """
        result = wikibase_helper.execute_query(query)
        self.violations = [[strip_url_part(e)] for [e] in result]
        self.violationsUpdated.emit()


CONSTRAINT_MAP = {
    "Q1585537": SingleValueConstraint,
    "Q1585538": ValueTypeConstraint,
    "Q1585539": SubjectTypeConstraint,
}


class ConstraintAnalyzer(QObject):

    constrainedPropertiesUpdated = pyqtSignal()
    focusedPropertyConstraintUpdated = pyqtSignal()

    def __init__(self, wikibase_helper):
        super().__init__()

        self.wikibase_helper = wikibase_helper
        self.constrained_properties = {}
        self.focused_property_constraint = None

    def update_constrained_properties(self):
        query = """
            SELECT ?subject ?subjectLabel ?object ?objectLabel
            WHERE
            {
                ?subject kpt:P85 ?object .
                SERVICE wikibase:label { bd:serviceParam wikibase:language "nl" . }
            }
            """
        query_result = self.wikibase_helper.execute_query(query)
        new_properties = {}
        for [prop_id, prop_label, cons_id, cons_label] in query_result[1:]:
            prop_id = strip_url_part(prop_id)
            cons_id = strip_url_part(cons_id)
            const_type = CONSTRAINT_MAP.get(cons_id)
            if not const_type:
                const_type = Constraint

            const_prop = new_properties.get(prop_id)
            if const_prop == None:
                const_prop = Property(prop_id, prop_label)
                new_properties[prop_id] = const_prop
            const_prop.constraints.append(const_type(cons_id, cons_label, const_prop))
        self.constrained_properties = new_properties
        self.constrainedPropertiesUpdated.emit()

    def get_constrained_properties_list_full(self):
        return [
            [p.identifier, p.label, c.identifier, c.label]
            for p in self.constrained_properties.values()
            for c in p.constraints
        ]

    def set_focused_property_constraint(self, prop_id, constraint_id):
        prop = self.constrained_properties.get(prop_id)
        if prop:
            for c in prop.constraints:
                if c.identifier == constraint_id:
                    self.focused_property_constraint = c
                    self.focusedPropertyConstraintUpdated.emit()
