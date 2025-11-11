from PySide6.QtCore import Signal, QObject

from .utils import stripUrlPart


class Property:
    def __init__(self, identifier, label):
        self.identifier = identifier
        self.label = label

    def __str__(self):
        return f"{self.label} ({self.identifier})"


class Constraint(QObject):
    violationsUpdated = Signal()
    qualifiersUpdated = Signal()

    def __init__(self, identifier, label, prop, wikibaseHelper):
        super().__init__()

        self.identifier = identifier
        self.implemented = False
        self.label = label
        self.property = prop
        self.qualifiersObtained = False
        self.wikibaseHelper = wikibaseHelper
        self.violations = None

        self.qualifiersUpdated.connect(self._onQualifiersUpdated)

    def __str__(self):
        return f"{self.label} ({self.identifier})"

    def pretty(self):
        return f'"{self.label}" ({self.identifier})\non "{self.property.label}" ({self.property.identifier})'

    def queryViolations(self):
        print(f"Querying violations not implemented for {self}")

    def _onQualifiersUpdated(self):
        self.qualifiersObtained = True


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Single_value
class SingleValueConstraint(Constraint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True

        self.separators = []

    def pretty(self):
        label = super().pretty()
        if len(self.separators):
            label += f"\nseperator(s): {[str(s) for s in self.separators]}"
        return label

    def queryQualifiers(self):
        if self.qualifiersObtained:
            return
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
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def _queryQualifiersResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            return
        for [identifier, label] in result[1:]:
            self.separators.append(Property(stripUrlPart(identifier), label))
        self.qualifiersUpdated.emit()

    def queryViolations(self):
        query = f"""
            SELECT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel ?valueCount
            WHERE
            {{
                {{
                    SELECT ?entity (COUNT(?value) AS ?valueCount)
                    WHERE
                    {{
                        ?entity kpp:{self.property.identifier} ?statement .
                        ?statement kpps:{self.property.identifier} ?value .
                        {'\n'.join(f'MINUS {{ ?statement kppq:{s.identifier} ?seperator }} .' for s in self.separators)}             
                    }}
                    GROUP BY ?entity
                    HAVING(?valueCount > 1)
                }}
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
            GROUP BY ?entity ?entityLabel ?valueCount
        """
        self.wikibaseHelper.executeQuery(query, self._queryViolationsResult)

    def _queryViolationsResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            return
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL, v] for [s, e, eL, v] in result
        ]
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Value_class
class ValueTypeConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True

        self.classes = []
        self.relation = None

    def pretty(self):
        label = super().pretty()
        if len(self.classes):
            label += f"\nclass(es): {[str(s) for s in self.classes]}"
        return label

    def queryQualifiers(self):
        if self.qualifiersObtained:
            return
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
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def _queryQualifiersResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            return
        for [classId, classLabel, relationId, relationLabel] in result[1:]:
            classId = stripUrlPart(classId)
            relationId = stripUrlPart(relationId)
            if relationId != "Q1585615":
                print(
                    f'ValueTypeConstraint for relation "{relationLabel}" is currently unsupported.'
                )
                self.relation = None
            self.classes.append(Property(classId, classLabel))
        self.relation = "P1"
        self.qualifiersUpdated.emit()

    def queryViolations(self):
        if self.relation != "P1":
            return
        query = f"""
            SELECT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel ?value ?valueLabel
            WHERE
            {{
                {{
                    SELECT DISTINCT ?entity ?value
                    WHERE
                    {{
                        ?entity kpt:{self.property.identifier} ?value .
                        {'\n'.join(f'MINUS {{ ?value kpt:{self.relation} kp:{c.identifier}}} .' for c in self.classes)}
                    }}
                }}
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
            GROUP BY ?entity ?entityLabel ?value ?valueLabel
        """
        self.wikibaseHelper.executeQuery(query, self._queryViolationsResult)

    def _queryViolationsResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            return
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL, stripUrlPart(v), vL]
            for [s, e, eL, v, vL] in result
        ]
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Subject_class
class SubjectTypeConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True

        self.classes = []
        self.relation = None

    def pretty(self):
        label = super().pretty()
        if len(self.classes):
            label += f"\nclass(es): {[str(s) for s in self.classes]}"
        return label

    def queryQualifiers(self):
        if self.qualifiersObtained:
            return
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
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def _queryQualifiersResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            return
        for [classId, classLabel, relationId, relationLabel] in result[1:]:
            classId = stripUrlPart(classId)
            relationId = stripUrlPart(relationId)
            if relationId != "Q1585615":
                print(
                    f'SubjectTypeConstraint for relation "{relationLabel}" is currently unsupported.'
                )
                self.relation = None
            self.classes.append(Property(classId, classLabel))
        self.relation = "P1"
        self.qualifiersUpdated.emit()

    def queryViolations(self):
        if self.relation != "P1":
            return
        query = f"""
            SELECT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel
            WHERE
            {{
                {{
                    SELECT DISTINCT ?entity
                    WHERE
                    {{
                        ?entity kpt:{self.property.identifier} ?value .
                        {'\n'.join(f'MINUS {{ ?entity kpt:{self.relation} kp:{c.identifier}}} .' for c in self.classes)}
                    }}
                }}
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
            GROUP BY ?entity ?entityLabel
        """
        self.wikibaseHelper.executeQuery(query, self._queryViolationsResult)

    def _queryViolationsResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            return
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
        ]
        self.violationsUpdated.emit()


class RequiredQualifierConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True

        self.requiredQualifier = None

    def pretty(self):
        label = super().pretty()
        label += f"\nrequired qualifier: {str(self.requiredQualifier)}"
        return label

    def queryQualifiers(self):
        if self.qualifiersObtained:
            return
        query = f"""
            SELECT DISTINCT ?prop ?propLabel
            WHERE
            {{
                ?statement kpps:P85 kp:Q1585540 .
                kp:{self.property.identifier} kpp:P85 ?statement .
                OPTIONAL {{ ?statement kppq:P88 ?prop }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def _queryQualifiersResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            return
        for [propId, propLabel] in result[1:]:
            propId = stripUrlPart(propId)
            self.requiredQualifier = Property(propId, propLabel)
        self.qualifiersUpdated.emit()

    def queryViolations(self):
        query = f"""
            SELECT DISTINCT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel
            WHERE
            {{
                {{
                    SELECT DISTINCT ?entity
                    WHERE
                    {{
                        ?entity kpp:{self.property.identifier} ?statement .
                        FILTER NOT EXISTS {{ ?statement kppq:{self.requiredQualifier.identifier} ?val }}
                    }}
                }}
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
            GROUP BY ?entity ?entityLabel
        """
        self.wikibaseHelper.executeQuery(query, self._queryViolationsResult)

    def _queryViolationsResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            return
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
        ]
        self.violationsUpdated.emit()


CONSTRAINT_MAP = {
    "Q1585537": SingleValueConstraint,
    "Q1585538": ValueTypeConstraint,
    "Q1585539": SubjectTypeConstraint,
    "Q1585540": RequiredQualifierConstraint,
}


class ConstraintAnalyzer(QObject):

    constrainedPropertiesUpdated = Signal()
    focusedPropertyConstraintUpdated = Signal()

    def __init__(self, wikibaseHelper):
        super().__init__()

        self.wikibaseHelper = wikibaseHelper
        self.constraints = {}
        self.focusedConstraint = None

    def updateConstraints(self):
        query = """
            SELECT ?subject ?subjectLabel ?object ?objectLabel
            WHERE
            {
                ?subject kpt:P85 ?object .
                SERVICE wikibase:label { bd:serviceParam wikibase:language "nl" . }
            }
            """
        self.wikibaseHelper.executeQuery(query, self._updateConstraintsResult)

    def _updateConstraintsResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            return
        self.constraints = {}
        for [propId, propLabel, consId, consLabel] in result[1:]:
            propId = stripUrlPart(propId)
            consId = stripUrlPart(consId)
            constType = CONSTRAINT_MAP.get(consId)
            if not constType:
                constType = Constraint

            constraint = constType(
                consId, consLabel, Property(propId, propLabel), self.wikibaseHelper
            )

            self.constraints[consId, propId] = constraint

        self.constrainedPropertiesUpdated.emit()

    def getConstraintsListFull(self):
        return [
            [
                c.property.identifier,
                c.property.label,
                c.identifier,
                c.label,
                c.implemented,
            ]
            for c in self.constraints.values()
        ]

    def setFocusedConstraint(self, propId, constraintId):
        constraint = self.constraints.get((constraintId, propId))
        if constraint:
            self.focusedConstraint = constraint
            self.focusedPropertyConstraintUpdated.emit()
