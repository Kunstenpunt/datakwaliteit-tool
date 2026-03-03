from typing import Optional, Sequence


from .base import (
    Constraint,
    Item,
    Property,
    ValidationInputCountType,
    ValidationMode,
)

from ..utils import idFromUrl
from ..wikibasehelper import WikibaseConfig


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Single_value
class SingleValueConstraint(Constraint):

    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label, prop, wikibaseConfig)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.separators: Sequence[Property] = []

    def pretty(self) -> str:
        label = super().pretty()
        if self.separators:
            label += f"\nseparator(s): {[str(s) for s in self.separators]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.separators = [
                Property(idFromUrl(identifier), label)
                for [identifier, label] in result[1:]
            ]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def getViolationsQuery(self) -> str:
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
                LIMIT {self.limit} OFFSET {self._offset}"""
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
                LIMIT {self.limit} OFFSET {self._offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" }}
            }}
            GROUP BY ?entity ?entityLabel ?valueCount"""

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(e), eL, v] for [s, e, eL, v] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Value_class
class ValueTypeConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label, prop, wikibaseConfig)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.classes: Sequence[Item] = []
        self.relation = ""

    def pretty(self) -> str:
        label = super().pretty()
        if self.classes:
            label += f"\nclass(es): {[str(s) for s in self.classes]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        classes = []

        try:
            for [classId, classLabel, relationId, relationLabel] in result[1:]:
                classId = idFromUrl(classId)
                relationId = idFromUrl(relationId)
                if relationLabel != "instance of":
                    print(
                        f'ValueTypeConstraint for relation "{relationLabel}" is currently unsupported.'
                    )
                    return
                classes.append(Item(classId, classLabel))
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.classes = classes
        self.relation = self._wikibaseConfig.getInstanceOfPid()
        self.qualifiersObtained = True

    def getViolationsQuery(self) -> str:
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
                LIMIT {self.limit} OFFSET {self._offset}"""
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
                LIMIT {self.limit} OFFSET {self._offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results
            
            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" }}
            }}"""

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(e), eL, idFromUrl(v), vL]
                for [s, e, eL, v, vL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Subject_class
class SubjectTypeConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label, prop, wikibaseConfig)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.ENTITIES

        self.classes: Sequence[Item] = []
        self.relation = ""

    def pretty(self) -> str:
        label = super().pretty()
        if self.classes is not None and len(self.classes):
            label += f"\nclass(es): {[str(s) for s in self.classes]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        classes = []
        try:
            for [classId, classLabel, relationId, relationLabel] in result[1:]:
                classId = idFromUrl(classId)
                relationId = idFromUrl(relationId)
                if relationLabel != "instance of":
                    print(
                        f'SubjectTypeConstraint for relation "{relationLabel}" is currently unsupported.'
                    )
                    return
                classes.append(Item(classId, classLabel))
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.classes = classes
        self.relation = self._wikibaseConfig.getInstanceOfPid()
        self.qualifiersObtained = True

    def getViolationsQuery(self) -> str:
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
                LIMIT {self.limit} OFFSET {self._offset}"""
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
                LIMIT {self.limit} OFFSET {self._offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" }}
            }}
            GROUP BY ?entity ?entityLabel"""

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(e), eL] for [s, e, eL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Required_qualifiers
class RequiredQualifierConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label, prop, wikibaseConfig)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.requiredQualifiers: Sequence[Property] = []

    def pretty(self) -> str:
        label = super().pretty()
        if self.requiredQualifiers:
            label += (
                f"\nrequired qualifiers: {[str(q) for q in self.requiredQualifiers]}"
            )
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.requiredQualifiers = [
                Property(idFromUrl(propId), propLabel)
                for [propId, propLabel] in result[1:]
            ]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def getViolationsQuery(self) -> str:
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
                LIMIT {self.limit} OFFSET {self._offset}"""
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
                LIMIT {self.limit} OFFSET {self._offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" }}
            }}"""

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(e), eL] for [s, e, eL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Qualifiers
class AllowedQualifiersConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label, prop, wikibaseConfig)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.allowedQualifiers: Sequence[Property] = []

    def pretty(self) -> str:
        label = super().pretty()
        if self.allowedQualifiers:
            label += f"\nallowed qualifiers: {[str(q) for q in self.allowedQualifiers]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.allowedQualifiers = [
                Property(idFromUrl(propId), propLabel)
                for [propId, propLabel] in result[1:]
            ]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def getViolationsQuery(self) -> str:
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
                LIMIT {self.limit} OFFSET {self._offset}"""
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
                LIMIT {self.limit} OFFSET {self._offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" }}
            }}"""

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(e), eL] for [s, e, eL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Conflicts_with
class ConflictsWithConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label, prop, wikibaseConfig)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.ENTITIES
        self.conflictingStatements: Sequence[tuple[Property, Optional[Item]]] = []

    def pretty(self) -> str:
        label = super().pretty()
        if self.conflictingStatements:
            label += f"\nconflicting statements: {[f"{str(p)}{" " + str(v) if v else ""}" for (p,v) in self.conflictingStatements]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.conflictingStatements = [
                (
                    Property(idFromUrl(propId), propLabel),
                    Item(valueId, valueLabel) if valueId else None,
                )
                for [propId, propLabel, valueId, valueLabel] in result[1:]
            ]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def getViolationsQuery(self) -> str:
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
                LIMIT {self.limit} OFFSET {self._offset}"""
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
                        EXISTS {{ ?entity kpt:{p.identifier} {"kp:" + v.identifier if v else "[]"} }}""" for (p,v) in self.conflictingStatements)
                    }
                    )
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self._offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" }}
            }}
            GROUP BY ?entity ?entityLabel"""

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(e), eL] for [s, e, eL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Unique_value
class DistinctValuesConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label, prop, wikibaseConfig)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.separators: Sequence[Property] = []

    def pretty(self) -> str:
        label = super().pretty()
        if self.separators:
            label += f"\nseparator(s): {[str(s) for s in self.separators]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.separators = [
                Property(idFromUrl(identifier), label)
                for [identifier, label] in result[1:]
            ]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        if self.separators:
            print(
                "Warning: validation hasn't been tested yet with separators, could explode violently."
            )
        self.qualifiersObtained = True

    def getViolationsQuery(self) -> str:
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
                LIMIT {self.limit} OFFSET {self._offset}"""
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
                LIMIT {self.limit} OFFSET {self._offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results


            WHERE
            {{
                INCLUDE %results
                ?statement kpps:{self.property.identifier} ?value .
                ?entity kpp:{self.property.identifier} ?statement .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" . }}
            }}"""

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(e), e_l, idFromUrl(v), v_l]
                for [s, e, e_l, v, v_l] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Format
class FormatConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label, prop, wikibaseConfig)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.format = ""

    def pretty(self) -> str:
        label = super().pretty()
        if self.format:
            label += f"\nformat: {self.format}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.format = result[1][0]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def getViolationsQuery(self) -> str:
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
                LIMIT {self.limit} OFFSET {self._offset}"""
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
                LIMIT {self.limit} OFFSET {self._offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" }}
            }}"""

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [
                    idFromUrl(s),
                    idFromUrl(e),
                    e_l,
                    v,
                ]
                for [s, e, e_l, v] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Item
class ItemRequiresStatementConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label, prop, wikibaseConfig)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.ENTITIES
        self.requiredStatements: dict[str, tuple[Property, list[Item]]] = {}

    def pretty(self) -> str:
        label = super().pretty()
        if self.requiredStatements:
            label += f"\nrequiredStatement: {[f"{str(s[0])} = " + ", ".join(str(v) for v in s[1]) for s in self.requiredStatements.values()]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        self.requiredStatements = {}
        try:
            for [propId, propLabel, valueId, valueLabel] in result[1:]:
                prop = Property(idFromUrl(propId), propLabel)
                if not (prop.identifier in self.requiredStatements):
                    self.requiredStatements[prop.identifier] = (prop, [])
                if valueId != None:
                    value = Item(idFromUrl(valueId), valueLabel)
                    self.requiredStatements[prop.identifier][1].append(value)
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def getViolationsQuery(self) -> str:
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
                LIMIT {self.limit} OFFSET {self._offset}"""
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
                        NOT EXISTS {{ ?entity kpt:{s[0].identifier} ?v . {f"VALUES ?v {{{" ".join("kp:" + v.identifier for v in s[1])}}}" if s[1] else ""} }}""" for s in self.requiredStatements.values())
                    }
                    )
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self._offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                ?entity kpp:{self.property.identifier} ?statement
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" }}
            }}
            GROUP BY ?entity ?entityLabel"""

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(e), eL] for [s, e, eL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Target_required_claim
class ValueRequiresStatementConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label, prop, wikibaseConfig)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS
        self.requiredStatements: dict[str, tuple[Property, list[Item]]] = {}

    def pretty(self) -> str:
        label = super().pretty()
        if self.requiredStatements:
            label += f"\nrequiredStatement: {[f"{str(s[0])} = " + ", ".join(str(v) for v in s[1]) for s in self.requiredStatements.values()]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        self.requiredStatements = {}
        try:
            for [propId, propLabel, valueId, valueLabel] in result[1:]:
                prop = Property(idFromUrl(propId), propLabel)
                if not (prop.identifier in self.requiredStatements):
                    self.requiredStatements[prop.identifier] = (prop, [])
                if valueId != None:
                    value = Item(idFromUrl(valueId), valueLabel)
                    self.requiredStatements[prop.identifier][1].append(value)
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def getViolationsQuery(self) -> str:
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
                LIMIT {self.limit} OFFSET {self._offset}"""
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
                        NOT EXISTS {{ ?value kpt:{s[0].identifier} ?v . {f"VALUES ?v {{{" ".join("kp:" + v.identifier for v in s[1])}}}" if s[1] else ""} }}""" for s in self.requiredStatements.values())
                    }
                    )
                }}{f"""{f"""
                ORDER BY ?entity"""
                    if self.sort else ""
                }
                LIMIT {self.limit} OFFSET {self._offset}""" 
                    if self.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" }}
            }}"""

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(e), eL] for [s, e, eL] in result
            ]
        except:
            return
