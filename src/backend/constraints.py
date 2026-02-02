from enum import Enum

from PySide6.QtCore import Signal, QObject

from .utils import stripUrlPart

# idee: eis dat alle entiteiten en properties die mappen op properties van wikidata hetzelfde label hebben in het Engels -> op die manier steeds correcte mapping


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
    PARTIAL = 3
    VALIDATED = 4
    FAILED = 5


class ValidationMode(Enum):
    NO_LIMIT = 0
    LIMIT_OUTPUT = 1
    LIMIT_INPUT = 2


class ValidationInputCountType(Enum):
    STATEMENTS = 0
    ENTITIES = 1
    OTHER = 2


class ConstraintHelper(QObject):
    qualifiersUpdated = Signal()
    violationsUpdated = Signal()

    inputCountUpdated = Signal()
    validationStateUpdated = Signal()

    def __init__(self, wikibaseHelper):
        super().__init__()
        self.constraint = None
        self.wikibaseHelper = wikibaseHelper

    def queryInputCount(self, c):
        if not c:
            return

        countType = c.validationInputCountType
        if countType == ValidationInputCountType.STATEMENTS:
            query = f"""
                SELECT (COUNT(*) as ?count)
                WHERE
                {{
                    ?entity kpp:{c.property.identifier} ?statement
                }}
            """
        elif countType == c.validationInputCountType.ENTITIES:
            query = f"""
                SELECT ?count
                WHERE
                {{
                    SERVICE wikibase:mwapi
                    {{
                        bd:serviceParam wikibase:endpoint "{self.wikibaseHelper.getPureUrl()}";
                            wikibase:api "Search"; wikibase:limit "once" ;
                            mwapi:srsearch "haswbstatement:{c.property.identifier}" ;
                            mwapi:srlimit "1" ; mwapi:srprop "" ; mwapi:srsort "none" ; mwapi:srnamespace "*" .
                        ?count wikibase:apiOutput '//searchinfo[1]/@totalhits'.
                    }}
                }}
            """
        else:
            print(f"Querying input count not implemented for {c}")
            return

        self.wikibaseHelper.executeQuery(query, self.queryInputCountResult, c)

    def queryInputCountResult(self):
        self.constraint = self.wikibaseHelper.callbackData
        if self.constraint is None:
            return

        result = self.wikibaseHelper.queryResult
        if result is None:
            return

        self.constraint.inputCount = int(result[1][0])
        self.inputCountUpdated.emit()

    def queryQualifiers(self, c):
        if c is None or c.qualifiersObtained:
            return

        query = c.getQualifiersQuery()
        if query is None:
            return

        self.wikibaseHelper.executeQuery(query, self.queryQualifiersResult, c)

    def queryQualifiersResult(self):
        self.constraint = self.wikibaseHelper.callbackData
        if not self.constraint:
            return

        result = self.wikibaseHelper.queryResult
        if not result:
            self.updateValidationState(ValidationState.FAILED)
            return

        self.constraint.updateQualifiers(result)

        if self.constraint.qualifiersObtained:
            self.qualifiersUpdated.emit()
        else:
            self.updateValidationState(ValidationState.FAILED)
            return
        

        # if this qualifier query was a prerequisite of a validation query, continue with that validation
        if self.constraint.doValidation:
            self.queryViolations(self.constraint)

    def queryViolations(self, c):
        self.constraint = c
        self.updateValidationState(ValidationState.VALIDATING)

        if not self.constraint.qualifiersObtained:
            self.constraint.doValidation = True
            self.queryQualifiers(self.constraint)
            return

        query = self.constraint.getViolationsQuery()
        if query is None:
            return

        self.wikibaseHelper.executeQuery(
            query, self.queryViolationsResult, self.constraint
        )

    def queryViolationsResult(self):
        self.constraint = self.wikibaseHelper.callbackData
        if not self.constraint:
            return

        result = self.wikibaseHelper.queryResult
        if not result:
            self.updateValidationState(ValidationState.FAILED)
            return

        self.constraint.updateViolations(result)

        self.constraint = self.constraint
        if self.constraint.violations is not None:
            self.updateValidationState(
                ValidationState.VALIDATED
                if self.constraint.validationMode == ValidationMode.NO_LIMIT
                else ValidationState.PARTIAL
            )
            self.violationsUpdated.emit()
        else:
            self.updateValidationState(ValidationState.FAILED)

    def updateValidationState(self, validationState):
        if self.constraint.validationState != validationState:
            self.constraint.validationState = validationState
            self.validationStateUpdated.emit()


class Constraint:
    def __init__(self, identifier, label, prop, wikibaseHelper):
        super().__init__()

        self.inputCount = -1
        self.validationState = ValidationState.UNVALIDATED

        self.doValidation = False
        self.identifier = identifier
        self.implemented = False
        self.label = label
        self.property = prop
        self.qualifiersObtained = False
        self.validationInputCountType = ValidationInputCountType.OTHER
        self.violations = None
        self.wikibaseHelper = wikibaseHelper

        self.limit = 100000
        self.offset = 0
        self.sort = False
        self.validationMode = ValidationMode.NO_LIMIT

    def __str__(self):
        return f"{self.label} ({self.identifier})"

    def __lt__(self, other):
        return [int(self.property.identifier[1:]), int(self.identifier[1:])] < [
            int(other.property.identifier[1:]),
            int(other.identifier[1:]),
        ]

    def getPage(self):
        return (self.offset / self.limit) + 1 if self.limit != 0 else 1

    def pretty(self):
        return f'"{self.label}" ({self.identifier})\non "{self.property.label}" ({self.property.identifier})'

    def getQualifiersQuery(self):
        print(f"Querying qualfiers not implemented for {self}")
        return None

    def getViolationsQuery(self):
        print(f"Querying violations not implemented for {self}")
        return None


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Single_value
class SingleValueConstraint(Constraint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.separators = None

    def pretty(self):
        label = super().pretty()
        if self.separators:
            label += f"\nseparator(s): {[str(s) for s in self.separators]}"
        return label

    def getQualifiersQuery(self):
        return f"""
            SELECT DISTINCT ?separator ?separatorLabel
            WHERE
            {{
                ?statement kpps:{self.wikibaseHelper.getPropertyConstraintPid()} kp:{self.identifier} .
                kp:{self.property.identifier} kpp:{self.wikibaseHelper.getPropertyConstraintPid()} ?statement .
                ?statement ?qualifier ?separator .
                BIND (IRI(replace(str(?qualifier), str(kppq:), str(kp:)))  AS ?qualifierEntity)
                SERVICE wikibase:label
                {{
                    bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                    ?qualifierEntity rdfs:label ?qualifierLabel .
                }}
                FILTER (str(?qualifierLabel) = "separator")
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" . }}
            }}
        """

    def updateQualifiers(self, result):
        if len(result) < 1:
            return

        self.separators = []
        for [identifier, label] in result[1:]:
            self.separators.append(Property(stripUrlPart(identifier), label))

        self.qualifiersObtained = True

    def getViolationsQuery(self):
        return f"""
            SELECT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel ?valueCount

            WITH
            {{
                SELECT ?entity ?statement ?value
                WHERE
                {{
                    ?entity kpp:{self.property.identifier} ?statement .
                    ?statement kpps:{self.property.identifier} ?value
                }}{f"""{f"""
                ORDER BY ?entity ?statement ?value"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}"""
                    if self.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input

            WITH
            {{
                SELECT ?entity (COUNT(?value) AS ?valueCount)
                WHERE
                {{
                    INCLUDE %input{"\n".join(f"""
                    OPTIONAL {{ ?statement kppq:{s.identifier} ?separator{i} }} .""" for (i, s) in enumerate(self.separators))
                    }
                }}
                GROUP BY ?entity { f", ".join(f"?separator{i}" for i in range(len(self.separators))) }
                HAVING(?valueCount > 1){ f"""{f"""
                ORDER BY ?entity ?value"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" }}
            }}
            GROUP BY ?entity ?entityLabel ?valueCount"""

    def updateViolations(self, result):
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL, v] for [s, e, eL, v] in result
        ]


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Value_class
class ValueTypeConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.classes = None
        self.relation = None

    def pretty(self):
        label = super().pretty()
        if self.classes is not None and len(self.classes):
            label += f"\nclass(es): {[str(s) for s in self.classes]}"
        return label

    def getQualifiersQuery(self):
        return f"""
            SELECT DISTINCT ?class ?classLabel ?relation ?relationLabel
            WHERE
            {{
                ?statement kpps:{self.wikibaseHelper.getPropertyConstraintPid()} kp:{self.identifier} .
                kp:{self.property.identifier} kpp:{self.wikibaseHelper.getPropertyConstraintPid()} ?statement .
                OPTIONAL
                {{
                    ?statement ?classQualifier ?class .
                    BIND (IRI(replace(str(?classQualifier), str(kppq:), str(kp:)))  AS ?classQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?classQualifierEntity rdfs:label ?classQualifierLabel .
                    }}
                    FILTER (str(?classQualifierLabel) = "class")
                }}
                OPTIONAL
                {{
                    ?statement ?relationQualifier ?relation .
                    BIND (IRI(replace(str(?relationQualifier), str(kppq:), str(kp:)))  AS ?relationQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?relationQualifierEntity rdfs:label ?relationQualifierLabel .
                        ?relation rdfs:label ?relationLabel .
                    }}
                    FILTER (str(?relationQualifierLabel) = "relation")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" . }}
            }}
        """

    def updateQualifiers(self, result):
        if len(result) < 1:
            return

        self.classes = []
        for [classId, classLabel, relationId, relationLabel] in result[1:]:
            classId = stripUrlPart(classId)
            relationId = stripUrlPart(relationId)
            if relationLabel != "instance of":
                print(
                    f'ValueTypeConstraint for relation "{relationLabel}" is currently unsupported.'
                )
                return
            self.classes.append(Property(classId, classLabel))
        self.relation = self.wikibaseHelper.getInstanceOfPid()
        self.qualifiersObtained = True

    def getViolationsQuery(self):
        return f"""
            SELECT ?statement ?entity ?entityLabel ?value ?valueLabel

            WITH
            {{
                SELECT ?statement ?value
                WHERE
                {{
                    ?statement kpps:{self.property.identifier} ?value
                }}{f"""{f"""
                ORDER BY ?statement ?value"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}"""
                    if self.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input

            WITH
            {{
                SELECT ?statement ?value
                WHERE
                {{
                    INCLUDE %input
                    MINUS {{ ?value kpt:{self.relation} ?x . VALUES ?x {{{" ".join(f"kp:{c.identifier}" for c in self.classes)}}} }}
                }}{f"""{f"""
                ORDER BY ?entity ?value"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results
            
            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" }}
            }}"""

    def updateViolations(self, result):
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL, stripUrlPart(v), vL]
            for [s, e, eL, v, vL] in result
        ]


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Subject_class
class SubjectTypeConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.ENTITIES

        self.classes = None
        self.relation = None

    def pretty(self):
        label = super().pretty()
        if self.classes is not None and len(self.classes):
            label += f"\nclass(es): {[str(s) for s in self.classes]}"
        return label

    def getQualifiersQuery(self):
        return f"""
            SELECT DISTINCT ?class ?classLabel ?relation ?relationLabel
            WHERE
            {{
                ?statement kpps:{self.wikibaseHelper.getPropertyConstraintPid()} kp:{self.identifier} .
                kp:{self.property.identifier} kpp:{self.wikibaseHelper.getPropertyConstraintPid()} ?statement .
                OPTIONAL
                {{
                    ?statement ?classQualifier ?class .
                    BIND (IRI(replace(str(?classQualifier), str(kppq:), str(kp:)))  AS ?classQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?classQualifierEntity rdfs:label ?classQualifierLabel .
                    }}
                    FILTER (str(?classQualifierLabel) = "class")
                }}
                OPTIONAL
                {{
                    ?statement ?relationQualifier ?relation .
                    BIND (IRI(replace(str(?relationQualifier), str(kppq:), str(kp:)))  AS ?relationQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?relationQualifierEntity rdfs:label ?relationQualifierLabel .
                        ?relation rdfs:label ?relationLabel .
                    }}
                    FILTER (str(?relationQualifierLabel) = "relation")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" . }}
            }}
        """

    def updateQualifiers(self, result):
        if len(result) < 1:
            return

        self.classes = []
        for [classId, classLabel, relationId, relationLabel] in result[1:]:
            classId = stripUrlPart(classId)
            relationId = stripUrlPart(relationId)
            if relationLabel != "instance of":
                print(
                    f'SubjectTypeConstraint for relation "{relationLabel}" is currently unsupported.'
                )
                return
            self.classes.append(Property(classId, classLabel))
        self.relation = self.wikibaseHelper.getInstanceOfPid()
        self.qualifiersObtained = True

    def getViolationsQuery(self):
        return f"""
            SELECT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel

            WITH
            {{
                SELECT DISTINCT ?entity
                WHERE
                {{
                    ?entity kpp:{self.property.identifier} []
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}"""
                if self.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input

            WITH
            {{
                SELECT ?entity
                WHERE
                {{
                    INCLUDE %input
                    MINUS {{ ?entity kpt:{self.relation} ?x . VALUES ?x {{{" ".join(f"kp:{c.identifier}" for c in self.classes)}}} }}
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" }}
            }}
            GROUP BY ?entity ?entityLabel"""

    def updateViolations(self, result):
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
        ]


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Required_qualifiers
class RequiredQualifierConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.requiredQualifiers = None

    def pretty(self):
        label = super().pretty()
        if self.requiredQualifiers:
            label += (
                f"\nrequired qualifiers: {[str(q) for q in self.requiredQualifiers]}"
            )
        return label

    def getQualifiersQuery(self):
        return f"""
            SELECT DISTINCT ?prop ?propLabel
            WHERE
            {{
                ?statement kpps:{self.wikibaseHelper.getPropertyConstraintPid()} kp:{self.identifier} .
                kp:{self.property.identifier} kpp:{self.wikibaseHelper.getPropertyConstraintPid()} ?statement .
                OPTIONAL
                {{
                    ?statement ?propertyQualifier ?prop .
                    BIND (IRI(replace(str(?propertyQualifier), str(kppq:), str(kp:)))  AS ?propertyQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?propertyQualifierEntity rdfs:label ?propertyQualifierLabel .
                    }}
                    FILTER (str(?propertyQualifierLabel) = "property")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" . }}
            }}
        """

    def updateQualifiers(self, result):
        if len(result) < 1:
            return

        self.requiredQualifiers = []
        for [propId, propLabel] in result[1:]:
            propId = stripUrlPart(propId)
            self.requiredQualifiers.append(Property(propId, propLabel))
        self.qualifiersObtained = True

    def getViolationsQuery(self):
        return f"""
            SELECT ?statement ?entity ?entityLabel
            
            WITH
            {{
                SELECT ?entity ?statement
                WHERE
                {{
                    ?entity kpp:{self.property.identifier} ?statement
                }}{f"""{f"""
                ORDER BY ?entity ?statement"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}"""
                    if self.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input

            WITH
            {{
                SELECT ?entity ?statement
                WHERE
                {{
                    INCLUDE %input
                {"".join(f"""
                    FILTER NOT EXISTS {{ ?statement kppq:{q.identifier} ?val }} .""" for q in self.requiredQualifiers)
                }
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" }}
            }}"""

    def updateViolations(self, result):
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
        ]


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Qualifiers
class AllowedQualifiersConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.allowedQualifiers = None

    def pretty(self):
        label = super().pretty()
        if self.allowedQualifiers:
            label += f"\nallowed qualifiers: {[str(q) for q in self.allowedQualifiers]}"
        return label

    def getQualifiersQuery(self):
        return f"""
            SELECT DISTINCT ?prop ?propLabel
            WHERE
            {{
                ?statement kpps:{self.wikibaseHelper.getPropertyConstraintPid()} kp:{self.identifier} .
                kp:{self.property.identifier} kpp:{self.wikibaseHelper.getPropertyConstraintPid()} ?statement .
                OPTIONAL
                {{
                    ?statement ?propertyQualifier ?prop .
                    BIND (IRI(replace(str(?propertyQualifier), str(kppq:), str(kp:)))  AS ?propertyQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?propertyQualifierEntity rdfs:label ?propertyQualifierLabel .
                    }}
                    FILTER (str(?propertyQualifierLabel) = "property")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" . }}
            }}
        """

    def updateQualifiers(self, result):
        if len(result) < 1:
            return

        self.allowedQualifiers = []
        for [propId, propLabel] in result[1:]:
            propId = stripUrlPart(propId)
            self.allowedQualifiers.append(Property(propId, propLabel))
        self.qualifiersObtained = True

    def getViolationsQuery(self):
        return f"""
            SELECT ?statement ?entity ?entityLabel

            WITH
            {{
                SELECT ?statement
                WHERE
                {{
                    [] kpp:{self.property.identifier} ?statement
                }}{f"""{f"""
                ORDER BY ?statement"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}"""
                    if self.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input

            WITH
            {{
                SELECT ?statement
                WHERE
                {{
                    INCLUDE %input
                    ?statement ?predicate [] .
                    [] wikibase:qualifier ?predicate .
                    FILTER(!(?predicate in ({", ".join(f"kppq:{q.identifier}" for q in self.allowedQualifiers)})))
                }}{f"""{f"""
                ORDER BY ?statement"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" }}
            }}"""

    def updateViolations(self, result):
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
        ]


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Conflicts_with
class ConflictsWithConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.ENTITIES
        # List of form [[Prop, Value], ...]
        self.conflictingStatements = None

    def pretty(self):
        label = super().pretty()
        if self.conflictingStatements:
            label += f"\nconflicting statements: {[f"{str(p)}{" " + str(v) if v else ""}" for [p,v] in self.conflictingStatements]}"
        return label

    def getQualifiersQuery(self):
        return f"""
            SELECT DISTINCT ?prop ?propLabel ?value ?valueLabel
            WHERE
            {{
                ?statement kpps:{self.wikibaseHelper.getPropertyConstraintPid()} kp:{self.identifier} .
                kp:{self.property.identifier} kpp:{self.wikibaseHelper.getPropertyConstraintPid()} ?statement .
                OPTIONAL
                {{
                    ?statement ?propertyQualifier ?prop .
                    BIND (IRI(replace(str(?propertyQualifier), str(kppq:), str(kp:)))  AS ?propertyQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?propertyQualifierEntity rdfs:label ?propertyQualifierLabel .
                    }}
                    FILTER (str(?propertyQualifierLabel) = "property")
                }}
                OPTIONAL
                {{
                    ?statement ?valueQualifier ?value .
                    BIND (IRI(replace(str(?valueQualifier), str(kppq:), str(kp:)))  AS ?valueQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?valueQualifierEntity rdfs:label ?valueQualifierLabel .
                    }}
                    FILTER (str(?valueQualifierLabel) = "item of property constraint")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" . }}
            }}
        """
        self.wikibaseHelper.executeQuery(query, self._queryQualifiersResult)

    def updateQualifiers(self, result):
        if len(result) < 1:
            return

        self.conflictingStatements = []
        for [propId, propLabel, valueId, valueLabel] in result[1:]:
            prop = Property(stripUrlPart(propId), propLabel)
            value = Item(valueId, valueLabel) if valueId else None
            self.conflictingStatements.append([prop, value])
        self.qualifiersObtained = True

    def getViolationsQuery(self):
        return f"""
            SELECT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel

            WITH
            {{
                SELECT DISTINCT ?entity
                WHERE
                {{
                    ?entity kpp:{self.property.identifier} []
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}"""
                if self.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input

            WITH
            {{
                SELECT ?entity
                WHERE
                {{
                    INCLUDE %input
                    FILTER({" ||".join(f"""
                        EXISTS {{ ?entity kpt:{p.identifier} {"kp:" + v.identifier if v else "[]"} }}""" for [p,v] in self.conflictingStatements)
                    }
                    )
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" }}
            }}
            GROUP BY ?entity ?entityLabel"""

    def updateViolations(self, result):
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
        ]


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Unique_value
class DistinctValuesConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.separators = None

    def pretty(self):
        label = super().pretty()
        if self.separators:
            label += f"\nseparator(s): {[str(s) for s in self.separators]}"
        return label

    def getQualifiersQuery(self):
        return f"""
            SELECT DISTINCT ?separator ?separatorLabel
            WHERE
            {{
                ?statement kpps:{self.wikibaseHelper.getPropertyConstraintPid()} kp:{self.identifier} .
                kp:{self.property.identifier} kpp:{self.wikibaseHelper.getPropertyConstraintPid()} ?statement .
                ?statement ?qualifier ?separator .
                BIND (IRI(replace(str(?qualifier), str(kppq:), str(kp:)))  AS ?qualifierEntity)
                SERVICE wikibase:label
                {{
                    bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                    ?qualifierEntity rdfs:label ?qualifierLabel .
                }}
                FILTER (str(?qualifierLabel) = "separator")
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" . }}
            }}
        """

    def updateQualifiers(self, result):
        if len(result) < 1:
            return

        self.separators = []
        for [identifier, label] in result[1:]:
            self.separators.append(Property(stripUrlPart(identifier), label))
        if self.separators:
            print(
                "Warning: validation hasn't been tested yet with separators, could explode violently."
            )
        self.qualifiersObtained = True

    def getViolationsQuery(self):
        return f"""
            # Note that the actual number of returned output rows will be
            # different from the choosen number if output is limited.
            #
            # The output limit limits the number of violating values,
            # so the actual number of output rows will be larger (at least
            # double the limit, as there must be more than 1 entity for each
            # value that offends distinct-values-constraint). We could limit
            # the final part of the query instead, but this would yield no
            # speed results at all as the heavy work happens in the query
            # before it. For other constraints the final step never adds extra
            # results, which is why there the limits do match the results.

            SELECT ?statement ?entity ?entityLabel ?value ?valueLabel

            WITH
            {{
                SELECT ?statement ?value
                WHERE
                {{
                    ?statement kpps:{self.property.identifier} ?value
                }}{f"""{f"""
                ORDER BY ?statement ?value"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}"""
                    if self.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input

            WITH
            {{
                SELECT ?value (COUNT(?statement) AS ?statementCount)
                WHERE
                {{
                    INCLUDE %input{"\n".join(f"""
                    OPTIONAL {{ ?statement kppq:{s.identifier} ?separator{i} }} .""" for (i, s) in enumerate(self.separators))
                    }
                }}
                GROUP BY ?value { f", ".join(f"?separator{i}" for i in range(len(self.separators))) }
                HAVING(?statementCount > 1){ f"""{f"""
                ORDER BY ?entity ?value"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results


            WHERE
            {{
                INCLUDE %results
                ?statement kpps:{self.property.identifier} ?value .
                ?entity kpp:{self.property.identifier} ?statement .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" . }}
            }}"""

    def updateViolations(self, result):
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), e_l, stripUrlPart(v), v_l]
            for [s, e, e_l, v, v_l] in result
        ]


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Format
class FormatConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.format = None

    def pretty(self):
        label = super().pretty()
        if self.format:
            label += f"\nformat: {self.format}"
        return label

    def getQualifiersQuery(self):
        return f"""
            SELECT DISTINCT ?format
            WHERE
            {{
                ?statement kpps:{self.wikibaseHelper.getPropertyConstraintPid()} kp:{self.identifier} .
                kp:{self.property.identifier} kpp:{self.wikibaseHelper.getPropertyConstraintPid()} ?statement .
                ?statement ?formatQualifier ?format .
                BIND (IRI(replace(str(?formatQualifier), str(kppq:), str(kp:)))  AS ?formatQualifierEntity) .
                SERVICE wikibase:label
                {{
                    bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                    ?formatQualifierEntity rdfs:label ?formatQualifierLabel .
                }}
                FILTER (str(?formatQualifierLabel) = "format as a regular expression")
            }}
        """

    def updateQualifiers(self, result):
        if len(result) < 2:
            return

        self.format = result[1][0]
        self.qualifiersObtained = True

    def getViolationsQuery(self):
        return f"""
            SELECT ?statement ?entity ?entityLabel ?value

            WITH
            {{
                SELECT ?statement ?value
                WHERE
                {{
                    ?statement kpps:{self.property.identifier} ?value
                }}{f"""{f"""
                ORDER BY ?statement ?value"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}"""
                    if self.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input

            WITH
            {{
                SELECT ?statement ?value
                WHERE
                {{
                    INCLUDE %input
                    FILTER(!REGEX(STR(?value), "{self.format.replace("\\", "\\\\")}"))
                }}{f"""{f"""
                ORDER BY ?entity ?value"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" }}
            }}"""

    def updateViolations(self, result):
        self.violations = [
            [
                stripUrlPart(s),
                stripUrlPart(e),
                e_l,
                v,
            ]
            for [s, e, e_l, v] in result
        ]


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Item
class ItemRequiresStatementConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.ENTITIES
        # Dictionary of form PROP_ID -> [PROP, VAL1, VAL2, ...]
        self.requiredStatements = None

    def pretty(self):
        label = super().pretty()
        if self.requiredStatements:
            label += f"\nrequiredStatement: {[f"{str(s[0])} = " + ", ".join(str(v) for v in s[1:]) for s in self.requiredStatements.values()]}"
        return label

    def getQualifiersQuery(self):
        return f"""
            SELECT DISTINCT ?prop ?propLabel ?value ?valueLabel
            WHERE
            {{
                ?statement kpps:{self.wikibaseHelper.getPropertyConstraintPid()} kp:{self.identifier} .
                kp:{self.property.identifier} kpp:{self.wikibaseHelper.getPropertyConstraintPid()} ?statement .
                OPTIONAL
                {{
                    ?statement ?propertyQualifier ?prop .
                    BIND (IRI(replace(str(?propertyQualifier), str(kppq:), str(kp:)))  AS ?propertyQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?propertyQualifierEntity rdfs:label ?propertyQualifierLabel .
                    }}
                    FILTER (str(?propertyQualifierLabel) = "property")
                }}
                OPTIONAL
                {{
                    ?statement ?valueQualifier ?value .
                    BIND (IRI(replace(str(?valueQualifier), str(kppq:), str(kp:)))  AS ?valueQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?valueQualifierEntity rdfs:label ?valueQualifierLabel .
                    }}
                    FILTER (str(?valueQualifierLabel) = "item of property constraint")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" . }}
            }}
        """

    def updateQualifiers(self, result):
        if len(result) < 1:
            return

        self.requiredStatements = {}
        for [propId, propLabel, valueId, valueLabel] in result[1:]:
            prop = Property(stripUrlPart(propId), propLabel)
            value = Item(stripUrlPart(valueId), valueLabel)
            if not (prop.identifier in self.requiredStatements):
                self.requiredStatements[prop.identifier] = [prop]
            if valueId != None:
                self.requiredStatements[prop.identifier].append(value)
        self.qualifiersObtained = True

    def getViolationsQuery(self):
        return f"""
            SELECT (SAMPLE(?statement) AS ?statement) ?entity ?entityLabel

            WITH
            {{
                SELECT DISTINCT ?entity
                WHERE
                {{
                    ?entity kpp:{self.property.identifier} []
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}"""
                if self.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input

            WITH
            {{
                SELECT ?entity
                WHERE
                {{
                    INCLUDE %input
                    FILTER({" ||".join(f"""
                        NOT EXISTS {{ ?entity kpt:{s[0].identifier} ?v . {f"VALUES ?v {{{" ".join("kp:" + v.identifier for v in s[1:])}}}" if len(s) > 1 else ""} }}""" for s in self.requiredStatements.values())
                    }
                    )
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" }}
            }}
            GROUP BY ?entity ?entityLabel"""

    def updateViolations(self, result):
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
        ]


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Target_required_claim
class ValueRequiresStatementConstraint(Constraint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS
        # Dictionary of form PROP_ID -> [PROP, VAL1, VAL2, ...]
        self.requiredStatements = None

    def pretty(self):
        label = super().pretty()
        if self.requiredStatements:
            label += f"\nrequiredStatement: {[f"{str(s[0])} = " + ", ".join(str(v) for v in s[1:]) for s in self.requiredStatements.values()]}"
        return label

    def getQualifiersQuery(self):
        return f"""
            SELECT DISTINCT ?prop ?propLabel ?value ?valueLabel
            WHERE
            {{
                ?statement kpps:{self.wikibaseHelper.getPropertyConstraintPid()} kp:{self.identifier} .
                kp:{self.property.identifier} kpp:{self.wikibaseHelper.getPropertyConstraintPid()} ?statement .
                OPTIONAL
                {{
                    ?statement ?propertyQualifier ?prop .
                    BIND (IRI(replace(str(?propertyQualifier), str(kppq:), str(kp:)))  AS ?propertyQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?propertyQualifierEntity rdfs:label ?propertyQualifierLabel .
                    }}
                    FILTER (str(?propertyQualifierLabel) = "property")
                }}
                OPTIONAL
                {{
                    ?statement ?valueQualifier ?value .
                    BIND (IRI(replace(str(?valueQualifier), str(kppq:), str(kp:)))  AS ?valueQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self.wikibaseHelper.getDefaultLanguage()}".
                        ?valueQualifierEntity rdfs:label ?valueQualifierLabel .
                    }}
                    FILTER (str(?valueQualifierLabel) = "item of property constraint")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" . }}
            }}
        """

    def updateQualifiers(self, result):
        if len(result) < 1:
            return

        self.requiredStatements = {}
        for [propId, propLabel, valueId, valueLabel] in result[1:]:
            prop = Property(stripUrlPart(propId), propLabel)
            value = Item(stripUrlPart(valueId), valueLabel)
            if not (prop.identifier in self.requiredStatements):
                self.requiredStatements[prop.identifier] = [prop]
            if valueId != None:
                self.requiredStatements[prop.identifier].append(value)

        self.qualifiersObtained = True

    def getViolationsQuery(self):
        return f"""
            SELECT ?statement ?value ?valueLabel

            WITH
            {{
                SELECT ?statement ?value
                WHERE
                {{
                    ?statement kpps:{self.property.identifier} ?value
                }}{f"""{f"""
                ORDER BY ?statement ?value"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}"""
                    if self.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input

            WITH
            {{
                SELECT ?statement ?value
                WHERE
                {{
                    INCLUDE %input
                    FILTER({" ||".join(f"""
                        NOT EXISTS {{ ?value kpt:{s[0].identifier} ?v . {f"VALUES ?v {{{" ".join("kp:" + v.identifier for v in s[1:])}}}" if len(s) > 1 else ""} }}""" for s in self.requiredStatements.values())
                    }
                    )
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self.offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self.wikibaseHelper.getDefaultLanguage() }" }}
            }}"""

    def updateViolations(self, result):
        self.violations = [
            [stripUrlPart(s), stripUrlPart(e), eL] for [s, e, eL] in result
        ]


CONSTRAINT_MAP = {
    "single-value constraint": SingleValueConstraint,
    "value-type constraint": ValueTypeConstraint,
    "subject type constraint": SubjectTypeConstraint,
    "required qualifier constraint": RequiredQualifierConstraint,
    "allowed qualifiers constraint": AllowedQualifiersConstraint,
    "conflicts-with constraint": ConflictsWithConstraint,
    "distinct-values constraint": DistinctValuesConstraint,
    "format constraint": FormatConstraint,
    "item-requires-statement constraint": ItemRequiresStatementConstraint,
    "value-requires-statement constraint": ValueRequiresStatementConstraint,
}


class ConstraintAnalyzer(QObject):

    constrainedPropertiesUpdated = Signal()
    constrainedPropertyValidationStateChanged = Signal()
    focusedPropertyConstraintUpdated = Signal()
    focusedPropertyConstraintInputCountUpdated = Signal()
    focusedPropertyConstraintQualifiersUpdated = Signal()
    focusedPropertyConstraintViolationsUpdated = Signal()
    validateAllDone = Signal()

    def __init__(self, wikibaseHelper):
        super().__init__()

        self.wikibaseHelper = wikibaseHelper

        self.constraintHelper = ConstraintHelper(self.wikibaseHelper)
        self.constraintHelper.inputCountUpdated.connect(self.onInputCountUpdated)
        self.constraintHelper.qualifiersUpdated.connect(self.onQualifiersUpdated)
        self.constraintHelper.violationsUpdated.connect(self.onViolationsUpdated)
        self.constraintHelper.validationStateUpdated.connect(self.validateNextInQueue)
        self.constraintHelper.validationStateUpdated.connect(self.constrainedPropertyValidationStateChanged)

        self.constraints = {}
        self.focusedConstraint = None
        self.validationQueue = []
        self.validatingQueue = False

    def updateConstraints(self):
        defaultLanguage = self.wikibaseHelper.getDefaultLanguage()
        constraintPid = self.wikibaseHelper.getPropertyConstraintPid()
        if defaultLanguage == "en":
            query = f"""
                SELECT ?subject ?subjectLabel ?object ?objectLabel
                WHERE
                {{
                    ?subject kpt:{constraintPid} ?object .
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
                }}
                """

        else:
            # We desire the english label for the constraint to match Q numbers correctly
            query = f"""
                SELECT ?subject ?subjectLabel ?object ?objectLabel
                WHERE
                {{
                    ?subject kpt:{ constraintPid } ?object .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "{defaultLanguage},en".
                        ?subject rdfs:label ?subjectLabel .
                    }}
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{defaultLanguage}".
                        ?object rdfs:label ?objectLabel .
                    }}
                }}
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
            constType = CONSTRAINT_MAP.get(consLabel)
            if not constType:
                constType = Constraint

            constraint = constType(
                consId, consLabel, Property(propId, propLabel), self.wikibaseHelper
            )

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
        self.constraintHelper.queryQualifiers(constraint)
        self.constraintHelper.queryInputCount(constraint)

    def validateFocusedConstraint(self, validationMode, limit, offset, sort):
        self.focusedConstraint.validationMode = validationMode
        self.focusedConstraint.limit = limit
        self.focusedConstraint.offset = offset
        self.focusedConstraint.sort = sort
        if self.validatingQueue:
            self.validationQueue.append(self.focusedConstraint)
        else:
            self.constraintHelper.queryViolations(self.focusedConstraint)

    def validatingAll(self):
        return len(self.validationQueue) != 0

    def stopValidatingAll(self):
        self.validationQueue = []
        self.validateAllDone.emit()

    def validateAll(self):
        self.validationQueue = list(self.constraints.values())
        self.validatingQueue = True
        self.validateNextInQueue()

    def validateNextInQueue(self):
        c = self.constraintHelper.constraint
        if c is not None and c.validationState == ValidationState.VALIDATING:
            return

        if not self.validationQueue:
            self.validateAllDone.emit()
            self.validatingQueue = False
            return
        constraint = self.validationQueue[-1]
        if (
            constraint.implemented
            and constraint.validationState == ValidationState.UNVALIDATED
        ):
            self.validationQueue.pop()
            self.constraintHelper.queryViolations(constraint)
        else:
            self.validationQueue.pop()
            self.validateNextInQueue()

    def onInputCountUpdated(self):
        c = self.constraintHelper.constraint
        if c == self.focusedConstraint:
            self.focusedPropertyConstraintInputCountUpdated.emit()

    def onQualifiersUpdated(self):
        c = self.constraintHelper.constraint
        if c == self.focusedConstraint:
            self.focusedPropertyConstraintQualifiersUpdated.emit()

    def onViolationsUpdated(self):
        c = self.constraintHelper.constraint
        if c == self.focusedConstraint:
            self.focusedPropertyConstraintViolationsUpdated.emit()
