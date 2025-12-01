from PySide6.QtCore import Signal, QObject
from enum import Enum

from .utils import stripUrlPart


class Item:
    def __init__(self, identifier, label):
        self.identifier = identifier
        self.label = label

    def __str__(self):
        if self.identifier == None and self.label == None:
            return "?"
        else:
            return f"{self.label} ({self.identifier})"


class Property(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ValidationState(Enum):
    UNVALIDATED = 1
    VALIDATING = 2
    VALIDATED = 3
    FAILED = 4

    strings = ["UNVALIDATED", "VALIDATING", "VALIDATED", "FAILED"]


class Constraint(QObject):
    violationsUpdated = Signal()
    qualifiersUpdated = Signal()
    validationStateChanged = Signal()

    def __init__(self, identifier, label, prop, wikibaseHelper):
        super().__init__()

        self._validationState = ValidationState.UNVALIDATED

        self.identifier = identifier
        self.implemented = False
        self.label = label
        self.property = prop
        self.qualifiersObtained = False
        self.wikibaseHelper = wikibaseHelper
        self.violations = None

        self.qualifiersUpdated.connect(self._onQualifiersUpdated)

    @property
    def validationState(self):
        return self._validationState

    @validationState.setter
    def validationState(self, value):
        self._validationState = value
        self.validationStateChanged.emit()

    def __str__(self):
        return f"{self.label} ({self.identifier})"

    def __lt__(self, other):
        return [int(self.property.identifier[1:]), int(self.identifier[1:])] < [
            int(other.property.identifier[1:]),
            int(other.identifier[1:]),
        ]

    def pretty(self):
        return f'"{self.label}" ({self.identifier})\non "{self.property.label}" ({self.property.identifier})'

    def queryQualifiers(self):
        print(f"Querying qualfiers not implemented for {self}")

    def queryViolations(self):
        self.validationState = ValidationState.VALIDATING
        if hasattr(self, "_queryViolations"):
            if not self.qualifiersObtained:
                self.qualifiersUpdated.connect(self._queryViolations)
                self.queryQualifiers()
            else:
                self._queryViolations()
        else:
            print(f"Querying violations not implemented for {self}")
            self.validationState = ValidationState.FAILED

    def _onQualifiersUpdated(self):
        self.qualifiersObtained = True


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Single_value
class SingleValueConstraint(Constraint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True

        self.separators = None

    def pretty(self):
        label = super().pretty()
        if self.separators:
            label += f"\nseparator(s): {[str(s) for s in self.separators]}"
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
            self.validationState = ValidationState.FAILED
            return
        self.separators = []
        for [identifier, label] in result[1:]:
            self.separators.append(Property(stripUrlPart(identifier), label))
        self.qualifiersUpdated.emit()

    def _queryViolations(self):
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
                        { f'\n{"    " * 6}'.join(
                        f'OPTIONAL {{ ?statement kppq:{s.identifier} ?separator{i} }} .' for (i, s) in enumerate(self.separators))
                        }
                    }}
                    GROUP BY ?entity { f", ".join(f"?separator{i}" for i in range(len(self.separators))) }
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
        if result:
            self.violations = [
                [stripUrlPart(s), stripUrlPart(e), eL, v] for [s, e, eL, v] in result
            ]
            self.validationState = ValidationState.VALIDATED
        else:
            self.validationState = ValidationState.FAILED
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
            self.validationState = ValidationState.FAILED
            return
        for [classId, classLabel, relationId, relationLabel] in result[1:]:
            classId = stripUrlPart(classId)
            relationId = stripUrlPart(relationId)
            if relationId != "Q1585615":
                print(
                    f'ValueTypeConstraint for relation "{relationLabel}" is currently unsupported.'
                )
                self.validationState = ValidationState.FAILED
                self.relation = None
            self.classes.append(Property(classId, classLabel))
        self.relation = "P1"
        self.qualifiersUpdated.emit()

    def _queryViolations(self):
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
                        { f'\n{"    " * 6}'.join(
                        f'MINUS {{ ?value kpt:{self.relation} kp:{c.identifier}}} .' for c in self.classes)
                        }
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
        if result:
            self.violations = [
                [stripUrlPart(s), stripUrlPart(e), eL, stripUrlPart(v), vL]
                for [s, e, eL, v, vL] in result
            ]
            self.validationState = ValidationState.VALIDATED
        else:
            self.validationState = ValidationState.FAILED
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
            self.validationState = ValidationState.FAILED
            return
        for [classId, classLabel, relationId, relationLabel] in result[1:]:
            classId = stripUrlPart(classId)
            relationId = stripUrlPart(relationId)
            if relationId != "Q1585615":
                print(
                    f'SubjectTypeConstraint for relation "{relationLabel}" is currently unsupported.'
                )
                self.validationState = ValidationState.FAILED
                self.relation = None
            self.classes.append(Property(classId, classLabel))
        self.relation = "P1"
        self.qualifiersUpdated.emit()

    def _queryViolations(self):
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
                        { f'\n{"    " * 6}'.join(
                        f'MINUS {{ ?entity kpt:{self.relation} kp:{c.identifier}}} .' for c in self.classes)
                        }
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
        if result:
            self.violations = [
                [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
            ]
            self.validationState = ValidationState.VALIDATED
        else:
            self.validationState = ValidationState.FAILED
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Required_qualifiers
class RequiredQualifierConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True

        self.requiredQualifiers = None

    def pretty(self):
        label = super().pretty()
        if self.requiredQualifiers:
            label += (
                f"\nrequired qualifiers: {[str(q) for q in self.requiredQualifiers]}"
            )
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
            self.validationState = ValidationState.FAILED
            return
        self.requiredQualifiers = []
        for [propId, propLabel] in result[1:]:
            propId = stripUrlPart(propId)
            self.requiredQualifiers.append(Property(propId, propLabel))
        self.qualifiersUpdated.emit()

    def _queryViolations(self):
        query = f"""
            SELECT DISTINCT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel
            WHERE
            {{
                {{
                    SELECT DISTINCT ?entity
                    WHERE
                    {{
                        ?entity kpp:{self.property.identifier} ?statement .
                        { f'\n{"    " * 6}'.join(
                        f'FILTER NOT EXISTS {{ ?statement kppq:{q.identifier} ?val }} .' for q in self.requiredQualifiers)
                        }
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
        if result:
            self.violations = [
                [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
            ]
            self.validationState = ValidationState.VALIDATED
        else:
            self.validationState = ValidationState.FAILED
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Qualifiers
class AllowedQualifiersConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True

        self.allowedQualifiers = None

    def pretty(self):
        label = super().pretty()
        if self.allowedQualifiers:
            label += f"\nallowed qualifiers: {[str(q) for q in self.allowedQualifiers]}"
        return label

    def queryQualifiers(self):
        if self.qualifiersObtained:
            return
        query = f"""
            SELECT DISTINCT ?prop ?propLabel
            WHERE
            {{
                ?statement kpps:P85 kp:Q1585541 .
                kp:{self.property.identifier} kpp:P85 ?statement .
                OPTIONAL {{ ?statement kppq:P88 ?prop }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def _queryQualifiersResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            self.validationState = ValidationState.FAILED
            return
        self.allowedQualifiers = []
        for [propId, propLabel] in result[1:]:
            propId = stripUrlPart(propId)
            self.allowedQualifiers.append(Property(propId, propLabel))
        self.qualifiersUpdated.emit()

    def _queryViolations(self):
        query = f"""
            SELECT DISTINCT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel
            WHERE
            {{
                {{
                    SELECT DISTINCT ?entity
                    WHERE
                    {{
                        ?entity kpp:{self.property.identifier} ?statement .
                        ?statement ?predicate [] .
                        [] wikibase:qualifier ?predicate .
                        FILTER(!(?predicate in ({", ".join(f"kppq:{q.identifier}" for q in self.allowedQualifiers)})))
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
        if result:
            self.violations = [
                [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
            ]
            self.validationState = ValidationState.VALIDATED
        else:
            self.validationState = ValidationState.FAILED
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Conflicts_with
class ConflictsWithConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        # List of form [[Prop, Value], ...]
        self.conflictingStatements = None

    def pretty(self):
        label = super().pretty()
        if self.conflictingStatements:
            label += f"\nconflicting statements: {[f"{str(p)}{" " + str(v) if v else ""}" for [p,v] in self.conflictingStatements]}"
        return label

    def queryQualifiers(self):
        if self.qualifiersObtained:
            return
        query = f"""
            SELECT DISTINCT ?prop ?propLabel ?value ?valueLabel
            WHERE
            {{
                ?statement kpps:P85 kp:Q1585646 .
                kp:{self.property.identifier} kpp:P85 ?statement .
                OPTIONAL {{ ?statement kppq:P88 ?prop }}
                OPTIONAL {{ ?statement kppq:P89 ?value}}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def _queryQualifiersResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            self.validationState = ValidationState.FAILED
            return
        self.conflictingStatements = []
        for [propId, propLabel, valueId, valueLabel] in result[1:]:
            prop = Property(stripUrlPart(propId), propLabel)
            value = Item(valueId, valueLabel) if valueId else None
            self.conflictingStatements.append([prop, value])
        self.qualifiersUpdated.emit()

    def _queryViolations(self):
        query = f"""
            SELECT DISTINCT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel
            WHERE
            {{
                {{
                    SELECT DISTINCT ?entity
                    WHERE
                    {{
                        ?entity kpp:{self.property.identifier} [] .
                        FILTER(
                            { f' ||\n{"    " * 7}'.join(
                            f'EXISTS {{ ?entity kpt:{p.identifier} {"kp:" + v.identifier if v else "[]"} }}' for [p,v] in self.conflictingStatements)
                            }
                        )
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
        if result:
            self.violations = [
                [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
            ]
            self.validationState = ValidationState.VALIDATED
        else:
            self.validationState = ValidationState.FAILED
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Unique_value
class DistinctValuesConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True

        self.separators = None

    def pretty(self):
        label = super().pretty()
        if self.separators:
            label += f"\nseparator(s): {[str(s) for s in self.separators]}"
        return label

    def queryQualifiers(self):
        if self.qualifiersObtained:
            return
        query = f"""
            SELECT DISTINCT ?pq_obj ?pq_objLabel
            WHERE
            {{
                ?statement kpps:P85 kp:Q1585647 .
                kp:{self.property.identifier} kpp:P85 ?statement .
                ?statement kppq:P90 ?pq_obj .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def _queryQualifiersResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            self.validationState = ValidationState.FAILED
            return
        self.separators = []
        for [identifier, label] in result[1:]:
            self.separators.append(Property(stripUrlPart(identifier), label))
        if self.separators:
            print(
                "Warning: validation hasn't been tested yet with separators, could explode violently."
            )
        self.qualifiersUpdated.emit()

    def _queryViolations(self):
        query = f"""
            SELECT ?statement ?entity ?entityLabel ?value ?valueLabel
            WHERE
            {{
                {{
                    SELECT ?value (COUNT(?statement) AS ?statementCount)
                    WHERE
                    {{
                        ?statement kpps:{self.property.identifier} ?value .
                        { f'\n{"    " * 6}'.join(
                        f'OPTIONAL {{ ?statement kppq:{s.identifier} ?separator{i} }} .' for (i, s) in enumerate(self.separators))
                        }
                    }}
                    GROUP BY ?value { f", ".join(f"?separator{i}" for i in range(len(self.separators))) }
                    HAVING(?statementCount > 1)
                }}
                ?statement kpps:{self.property.identifier} ?value .
                ?entity kpp:{self.property.identifier} ?statement .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryViolationsResult)

    def _queryViolationsResult(self):
        result = self.wikibaseHelper.queryResult
        if result:
            self.violations = [
                [stripUrlPart(s), stripUrlPart(e), e_l, stripUrlPart(v), v_l]
                for [s, e, e_l, v, v_l] in result
            ]
            self.validationState = ValidationState.VALIDATED
        else:
            self.validationState = ValidationState.FAILED
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Format
class FormatConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True

        self.format = None

    def pretty(self):
        label = super().pretty()
        if self.format:
            label += f"\nformat: {self.format}"
        return label

    def queryQualifiers(self):
        if self.qualifiersObtained:
            return
        query = f"""
            SELECT DISTINCT ?format
            WHERE
            {{
                ?statement kpps:P85 kp:Q1585648 .
                kp:{self.property.identifier} kpp:P85 ?statement .
                ?statement kppq:P96 ?format .
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def _queryQualifiersResult(self):
        result = self.wikibaseHelper.queryResult
        if not result or len(result) < 2:
            self.validationState = ValidationState.FAILED
            return
        self.format = result[1][0]
        self.qualifiersUpdated.emit()

    def _queryViolations(self):
        query = f"""
            SELECT ?statement ?entity ?entityLabel ?value
            WHERE
            {{
                {{
                    SELECT ?statement ?value
                    WHERE
                    {{
                        ?statement kpps:{self.property.identifier} ?value .
                        FILTER(!REGEX(STR(?value), "{self.format.replace("\\", "\\\\")}"))
                    }}
                }}
                ?entity kpp:{self.property.identifier} ?statement .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryViolationsResult)

    def _queryViolationsResult(self):
        result = self.wikibaseHelper.queryResult
        if result:
            self.violations = [
                [
                    stripUrlPart(s),
                    stripUrlPart(e),
                    e_l,
                    v,
                ]
                for [s, e, e_l, v] in result
            ]
            self.validationState = ValidationState.VALIDATED
        else:
            self.validationState = ValidationState.FAILED
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Item
class ItemRequiresStatementConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        # Dictionary of form PROP_ID -> [PROP, VAL1, VAL2, ...]
        self.requiredStatements = None

    def pretty(self):
        label = super().pretty()
        if self.requiredStatements:
            label += f"\nrequiredStatement: {[f"{str(s[0])} = " + ", ".join(str(v) for v in s[1:]) for s in self.requiredStatements.values()]}"
        return label

    def queryQualifiers(self):
        if self.qualifiersObtained:
            return
        query = f"""
            SELECT DISTINCT ?prop ?propLabel ?value ?valueLabel
            WHERE
            {{
                ?statement kpps:P85 kp:Q1585649 .
                kp:{self.property.identifier} kpp:P85 ?statement .
                OPTIONAL {{ ?statement kppq:P88 ?prop }}
                OPTIONAL {{ ?statement kppq:P89 ?value}}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def _queryQualifiersResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            self.validationState = ValidationState.FAILED
            return
        self.requiredStatements = {}
        for [propId, propLabel, valueId, valueLabel] in result[1:]:
            prop = Property(stripUrlPart(propId), propLabel)
            value = Item(stripUrlPart(valueId), valueLabel)
            if not (prop.identifier in self.requiredStatements):
                self.requiredStatements[prop.identifier] = [prop]
            if valueId != None:
                self.requiredStatements[prop.identifier].append(value)
        self.qualifiersUpdated.emit()

    def _queryViolations(self):
        query = f"""
            SELECT DISTINCT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel
            WHERE
            {{
                {{
                    SELECT DISTINCT ?entity
                    WHERE
                    {{
                        ?entity kpp:{self.property.identifier} [] .
                        FILTER(
                            { f' ||\n{"    " * 7}'.join(
                            f'NOT EXISTS {{ ?entity kpt:{s[0].identifier} ?v . {f"VALUES ?v {{{" ".join("kp:" + v.identifier for v in s[1:])}}}" if len(s) > 1 else ""} }}' for s in self.requiredStatements.values())
                            }
                        )
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
        if result:
            self.violations = [
                [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
            ]
            self.validationState = ValidationState.VALIDATED
        else:
            self.validationState = ValidationState.FAILED
        self.violationsUpdated.emit()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Target_required_claim
class ValueRequiresStatementConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        # Dictionary of form PROP_ID -> [PROP, VAL1, VAL2, ...]
        self.requiredStatements = None

    def pretty(self):
        label = super().pretty()
        if self.requiredStatements:
            label += f"\nrequiredStatement: {[f"{str(s[0])} = " + ", ".join(str(v) for v in s[1:]) for s in self.requiredStatements.values()]}"
        return label

    def queryQualifiers(self):
        if self.qualifiersObtained:
            return
        query = f"""
            SELECT DISTINCT ?prop ?propLabel ?value ?valueLabel
            WHERE
            {{
                ?statement kpps:P85 kp:Q1585650 .
                kp:{self.property.identifier} kpp:P85 ?statement .
                OPTIONAL {{ ?statement kppq:P88 ?prop }}
                OPTIONAL {{ ?statement kppq:P89 ?value}}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def _queryQualifiersResult(self):
        result = self.wikibaseHelper.queryResult
        if not result:
            self.validationState = ValidationState.FAILED
            return
        self.requiredStatements = {}
        for [propId, propLabel, valueId, valueLabel] in result[1:]:
            prop = Property(stripUrlPart(propId), propLabel)
            value = Item(stripUrlPart(valueId), valueLabel)
            if not (prop.identifier in self.requiredStatements):
                self.requiredStatements[prop.identifier] = [prop]
            if valueId != None:
                self.requiredStatements[prop.identifier].append(value)

        self.qualifiersUpdated.emit()

    def _queryViolations(self):
        query = f"""
            SELECT ?statement ?value ?valueLabel
            WHERE
            {{
                {{
                    SELECT DISTINCT ?statement ?value
                    WHERE
                    {{
                        ?statement kpps:{self.property.identifier} ?value .
                        FILTER(
                            { f' ||\n{"    " * 7}'.join(
                            f'NOT EXISTS {{ ?value kpt:{s[0].identifier} ?v . {f"VALUES ?v {{{" ".join("kp:" + v.identifier for v in s[1:])}}}" if len(s) > 1 else ""} }}' for s in self.requiredStatements.values())
                            }
                        )
                    }}
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl" . }}
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryViolationsResult)

    def _queryViolationsResult(self):
        result = self.wikibaseHelper.queryResult
        if result:
            self.violations = [
                [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
            ]
            self.validationState = ValidationState.VALIDATED
        else:
            self.validationState = ValidationState.FAILED
        self.violationsUpdated.emit()


CONSTRAINT_MAP = {
    "Q1585537": SingleValueConstraint,
    "Q1585538": ValueTypeConstraint,
    "Q1585539": SubjectTypeConstraint,
    "Q1585540": RequiredQualifierConstraint,
    "Q1585541": AllowedQualifiersConstraint,
    "Q1585646": ConflictsWithConstraint,
    "Q1585647": DistinctValuesConstraint,
    "Q1585648": FormatConstraint,
    "Q1585649": ItemRequiresStatementConstraint,
    "Q1585650": ValueRequiresStatementConstraint,
}


class ConstraintAnalyzer(QObject):

    constrainedPropertiesUpdated = Signal()
    constrainedPropertyValidationStateChanged = Signal()
    focusedPropertyConstraintUpdated = Signal()
    validateAllDone = Signal()

    def __init__(self, wikibaseHelper):
        super().__init__()

        self.wikibaseHelper = wikibaseHelper
        self.constraints = {}
        self.focusedConstraint = None
        self.validationQueue = []

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
            constraint.validationStateChanged.connect(
                self.constrainedPropertyValidationStateChanged
            )

            constraint.qualifiersUpdated.connect(self.validateNextInQueue)
            constraint.violationsUpdated.connect(self.validateNextInQueue)

            self.constraints[consId, propId] = constraint

        self.constrainedPropertiesUpdated.emit()

    def getConstraintsListFull(self):
        return sorted(
            [
                [
                    c.property.identifier,
                    c.property.label,
                    c.identifier,
                    c.label,
                    c.implemented,
                    c.validationState,
                ]
                for c in self.constraints.values()
            ]
        )

    def setFocusedConstraint(self, propId, constraintId):
        constraint = self.constraints.get((constraintId, propId))
        if constraint:
            self.focusedConstraint = constraint
            self.focusedPropertyConstraintUpdated.emit()

    def validatingAll(self):
        return len(self.validationQueue) != 0

    def stopValidatingAll(self):
        self.validationQueue = []
        self.validateAllDone.emit()

    def validateAll(self):
        self.validationQueue = list(self.constraints.values())
        self.validateNextInQueue()

    def validateNextInQueue(self):
        if not self.validationQueue:
            self.validateAllDone.emit()
            return
        constraint = self.validationQueue[-1]
        if constraint.implemented and constraint.validationState == ValidationState.UNVALIDATED:
            if not constraint.qualifiersObtained:
                constraint.queryQualifiers()
            else:
                self.validationQueue.pop()
                constraint.queryViolations()
        else:
            self.validationQueue.pop()
            self.validateNextInQueue()
