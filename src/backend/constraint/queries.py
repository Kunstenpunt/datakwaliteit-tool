from enum import auto, Enum
from typing import Optional

from .base import Constraint, ValidationInputCountType, ValidationMode
from .constraint_types import *
from ..wikibasehelper import WikibaseConfig


class ViolationsQueryInputType(Enum):
    ITEM = auto()
    ITEM_STATEMENT = auto()
    ITEM_STATEMENT_VALUE = auto()
    STATEMENT = auto()
    STATEMENT_VALUE = auto()


class QueryBuilder:

    def __init__(self, wikibaseConfig: WikibaseConfig):
        self._wikibaseConfig = wikibaseConfig

    def buildConstrainedPropertiesQuery(self) -> str:
        defaultLanguage = self._wikibaseConfig.getDefaultLanguage()
        constraintPid = self._wikibaseConfig.getPropertyConstraintPid()
        if defaultLanguage == "en":
            return f"""
                SELECT ?subject ?subjectLabel ?object ?objectLabel
                WHERE
                {{
                    ?subject kpt:{constraintPid} ?object .
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
                }}
                """

        else:
            # We desire the english label for the constraint to match Q numbers correctly
            return f"""
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

    def buildInputCountQuery(self, constraint: Constraint) -> Optional[str]:
        countType = constraint.validationInputCountType
        if countType == ValidationInputCountType.STATEMENTS:
            return f"""
                SELECT (COUNT(*) as ?count)
                WHERE
                {{
                    ?item kpp:{constraint.property.identifier} ?statement
                }}
            """
        elif countType == constraint.validationInputCountType.ENTITIES:
            return f"""
                SELECT ?count
                WHERE
                {{
                    SERVICE wikibase:mwapi
                    {{
                        bd:serviceParam wikibase:endpoint "{self._wikibaseConfig.getPureUrl()}";
                            wikibase:api "Search"; wikibase:limit "once" ;
                            mwapi:srsearch "haswbstatement:{constraint.property.identifier}" ;
                            mwapi:srlimit "1" ; mwapi:srprop "" ; mwapi:srsort "none" ; mwapi:srnamespace "*" .
                        ?count wikibase:apiOutput '//searchinfo[1]/@totalhits'.
                    }}
                }}
            """
        else:
            return None

    def buildExceptionIdsQuery(self, constraint: Constraint) -> str:
        return f"""
            SELECT ?exception
            WHERE
            {{
                kp:{constraint.property.identifier} kpp:{self._wikibaseConfig.getPropertyConstraintPid()} ?statement .
                ?statement kpps:{self._wikibaseConfig.getPropertyConstraintPid()} kp:{constraint.identifier} .
                ?statement ?exceptionQualifier ?exception .

                BIND (IRI(replace(str(?exceptionQualifier), str(kppq:), str(kp:)))  AS ?exceptionQualifierItem) .
                SERVICE wikibase:label
                {{
                    bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                    ?exceptionQualifierItem rdfs:label ?exceptionQualifierLabel .
                }}
                FILTER (str(?exceptionQualifierLabel) = "exception to constraint")

                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" . }}
            }}
        """

    def buildQualifiersQuery(self, constraint: Constraint) -> Optional[str]:
        qualifiersQueryMapping = {
            SingleValueConstraint: self._buildSeparatorQuery,
            ValueTypeConstraint: self._buildClassRelationQuery,
            SubjectTypeConstraint: self._buildClassRelationQuery,
            RequiredQualifierConstraint: self._buildPropQuery,
            AllowedQualifiersConstraint: self._buildPropQuery,
            ConflictsWithConstraint: self._buildPropValueQuery,
            DistinctValuesConstraint: self._buildSeparatorQuery,
            FormatConstraint: self._buildFormatQuery,
            ItemRequiresStatementConstraint: self._buildPropValueQuery,
            ValueRequiresStatementConstraint: self._buildPropValueQuery,
        }
        constraintType = type(constraint)
        if constraintType in qualifiersQueryMapping:
            return qualifiersQueryMapping[constraintType](constraint)
        else:
            print(f"Querying qualifiers not implemented for {constraint}")
            return None

    def _buildClassRelationQuery(self, constraint: Constraint) -> str:
        return f"""
            SELECT DISTINCT ?class ?classLabel ?relation ?relationLabel
            WHERE
            {{
                ?statement kpps:{self._wikibaseConfig.getPropertyConstraintPid()} kp:{constraint.identifier} .
                kp:{constraint.property.identifier} kpp:{self._wikibaseConfig.getPropertyConstraintPid()} ?statement .
                OPTIONAL
                {{
                    ?statement ?classQualifier ?class .
                    BIND (IRI(replace(str(?classQualifier), str(kppq:), str(kp:)))  AS ?classQualifierItem) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                        ?classQualifierItem rdfs:label ?classQualifierLabel .
                    }}
                    FILTER (str(?classQualifierLabel) = "class")
                }}
                OPTIONAL
                {{
                    ?statement ?relationQualifier ?relation .
                    BIND (IRI(replace(str(?relationQualifier), str(kppq:), str(kp:)))  AS ?relationQualifierItem) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                        ?relationQualifierItem rdfs:label ?relationQualifierLabel .
                        ?relation rdfs:label ?relationLabel .
                    }}
                    FILTER (str(?relationQualifierLabel) = "relation")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" . }}
            }}
        """

    def _buildFormatQuery(self, constraint: Constraint) -> str:
        return f"""
            SELECT DISTINCT ?format
            WHERE
            {{
                ?statement kpps:{self._wikibaseConfig.getPropertyConstraintPid()} kp:{constraint.identifier} .
                kp:{constraint.property.identifier} kpp:{self._wikibaseConfig.getPropertyConstraintPid()} ?statement .
                ?statement ?formatQualifier ?format .
                BIND (IRI(replace(str(?formatQualifier), str(kppq:), str(kp:)))  AS ?formatQualifierItem) .
                SERVICE wikibase:label
                {{
                    bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                    ?formatQualifierItem rdfs:label ?formatQualifierLabel .
                }}
                FILTER (str(?formatQualifierLabel) = "format as a regular expression")
            }}
        """

    def _buildPropQuery(self, constraint: Constraint) -> str:
        return f"""
            SELECT DISTINCT ?prop ?propLabel
            WHERE
            {{
                ?statement kpps:{self._wikibaseConfig.getPropertyConstraintPid()} kp:{constraint.identifier} .
                kp:{constraint.property.identifier} kpp:{self._wikibaseConfig.getPropertyConstraintPid()} ?statement .
                OPTIONAL
                {{
                    ?statement ?propertyQualifier ?prop .
                    BIND (IRI(replace(str(?propertyQualifier), str(kppq:), str(kp:)))  AS ?propertyQualifierItem) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                        ?propertyQualifierItem rdfs:label ?propertyQualifierLabel .
                    }}
                    FILTER (str(?propertyQualifierLabel) = "property")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" . }}
            }}
        """

    def _buildPropValueQuery(self, constraint: Constraint) -> str:
        return f"""
            SELECT DISTINCT ?prop ?propLabel ?value ?valueLabel
            WHERE
            {{
                ?statement kpps:{self._wikibaseConfig.getPropertyConstraintPid()} kp:{constraint.identifier} .
                kp:{constraint.property.identifier} kpp:{self._wikibaseConfig.getPropertyConstraintPid()} ?statement .
                OPTIONAL
                {{
                    ?statement ?propertyQualifier ?prop .
                    BIND (IRI(replace(str(?propertyQualifier), str(kppq:), str(kp:)))  AS ?propertyQualifierItem) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                        ?propertyQualifierItem rdfs:label ?propertyQualifierLabel .
                    }}
                    FILTER (str(?propertyQualifierLabel) = "property")
                }}
                OPTIONAL
                {{
                    ?statement ?valueQualifier ?value .
                    BIND (IRI(replace(str(?valueQualifier), str(kppq:), str(kp:)))  AS ?valueQualifierItem) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                        ?valueQualifierItem rdfs:label ?valueQualifierLabel .
                    }}
                    FILTER (str(?valueQualifierLabel) = "item of property constraint")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" . }}
            }}
        """

    def _buildSeparatorQuery(self, constraint: Constraint) -> str:
        return f"""
            SELECT DISTINCT ?separator ?separatorLabel
            WHERE
            {{
                ?statement kpps:{self._wikibaseConfig.getPropertyConstraintPid()} kp:{constraint.identifier} .
                kp:{constraint.property.identifier} kpp:{self._wikibaseConfig.getPropertyConstraintPid()} ?statement .
                ?statement ?qualifier ?separator .
                BIND (IRI(replace(str(?qualifier), str(kppq:), str(kp:)))  AS ?qualifierItem)
                SERVICE wikibase:label
                {{
                    bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                    ?qualifierItem rdfs:label ?qualifierLabel .
                }}
                FILTER (str(?qualifierLabel) = "separator")
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" . }}
            }}
        """

    def buildViolationsQuery(self, constraint: Constraint) -> Optional[str]:
        violationsQueryMapping = {
            SingleValueConstraint: self._buildSingleValueConstraintViolationsQuery,
            ValueTypeConstraint: self._buildValueTypeConstraintViolationsQuery,
            SubjectTypeConstraint: self._buildSubjectTypeConstraintViolationsQuery,
            RequiredQualifierConstraint: self._buildRequiredQualifierConstraintViolationsQuery,
            ValueRequiresStatementConstraint: self._buildValueRequiresStatementConstraintViolationsQuery,
            AllowedQualifiersConstraint: self._buildAllowedQualifierConstraintViolationsQuery,
            ConflictsWithConstraint: self._buildConflictsWithConstraintViolationsQuery,
            DistinctValuesConstraint: self._buildDistinctValuesConstraintViolationsQuery,
            FormatConstraint: self._buildFormatConstraintViolationsQuery,
            ItemRequiresStatementConstraint: self._buildItemRequiresStatementConstraintViolationsQuery,
            ValueRequiresStatementConstraint: self._buildValueRequiresStatementConstraintViolationsQuery,
        }

        constraintType = type(constraint)
        if constraintType in violationsQueryMapping:
            return violationsQueryMapping[constraintType](constraint)  # type: ignore
        else:
            print(f"Querying violations not implemented for {constraint}")
            return None

    def _buildSingleValueConstraintViolationsQuery(
        self,
        constraint: SingleValueConstraint,
    ) -> str:
        outerSelection = (
            "(SAMPLE(?statement) AS ?statement) ?item ?itemLabel ?valueCount"
        )
        inputPart = self._buildViolationsQueryInput(
            constraint, ViolationsQueryInputType.ITEM_STATEMENT_VALUE
        )
        innerSelection = "?item (COUNT(?value) AS ?valueCount)"
        conditions = "\n".join(
            f"""
                    OPTIONAL {{ ?statement kppq:{s.identifier} ?separator{i} }} ."""
            for (i, s) in enumerate(constraint.separators)
        )
        innerGroupBy = f"?item {f" ".join(f"?separator{i}" for i in range(len(constraint.separators)))}"
        innerHaving = "?valueCount > 1"
        innerOrderBy = "?item ?valueCount"
        finalConditions = f"""
                ?item kpp:{constraint.property.identifier} ?statement ."""
        outerGroupBy = "?item ?itemLabel ?valueCount"
        return self._buildViolationsQuery(
            constraint,
            inputPart,
            outerSelection,
            innerSelection,
            conditions,
            innerGroupBy=innerGroupBy,
            innerHaving=innerHaving,
            innerOrderBy=innerOrderBy,
            finalConditions=finalConditions,
            outerGroupBy=outerGroupBy,
        )

    def _buildValueTypeConstraintViolationsQuery(
        self, constraint: ValueTypeConstraint
    ) -> str:
        if constraint.relation != RelationType.INSTANCE_OF:
            return ""
        relation = self._wikibaseConfig.getInstanceOfPid()
        outerSelection = "?statement ?item ?itemLabel ?value ?valueLabel"
        inputPart = self._buildViolationsQueryInput(
            constraint, ViolationsQueryInputType.STATEMENT_VALUE
        )
        innerSelection = "?item ?value ?statement"
        conditions = f"""
                    MINUS {{ ?value kpt:{relation} ?x . VALUES ?x {{{" ".join(f"kp:{c.identifier}" for c in constraint.classes)}}} }}"""
        finalConditions = f"""
                ?item kpp:{constraint.property.identifier} ?statement ."""
        return self._buildViolationsQuery(
            constraint,
            inputPart,
            outerSelection,
            innerSelection,
            conditions,
            finalConditions=finalConditions,
        )

    def _buildSubjectTypeConstraintViolationsQuery(
        self, constraint: SubjectTypeConstraint
    ) -> str:
        if constraint.relation != RelationType.INSTANCE_OF:
            return ""
        relation = self._wikibaseConfig.getInstanceOfPid()
        outerSelection = "(SAMPLE(?statement) AS ?statement) ?item ?itemLabel"
        inputPart = self._buildViolationsQueryInput(
            constraint, ViolationsQueryInputType.ITEM
        )
        innerSelection = "?item"
        conditions = f"""
                    MINUS {{ ?item kpt:{relation} ?x . VALUES ?x {{{" ".join(f"kp:{c.identifier}" for c in constraint.classes)}}} }}"""
        outerGroupBy = "?item ?itemLabel"
        finalConditions = f"""
                ?item kpp:{constraint.property.identifier} ?statement ."""
        return self._buildViolationsQuery(
            constraint,
            inputPart,
            outerSelection,
            innerSelection,
            conditions,
            outerGroupBy=outerGroupBy,
            finalConditions=finalConditions,
        )

    def _buildRequiredQualifierConstraintViolationsQuery(
        self, constraint: RequiredQualifierConstraint
    ) -> str:
        outerSelection = "?statement ?item ?itemLabel"
        inputPart = self._buildViolationsQueryInput(
            constraint, ViolationsQueryInputType.ITEM_STATEMENT
        )
        innerSelection = "?item ?statement"
        conditions = "".join(
            f"""
                    FILTER NOT EXISTS {{ ?statement kppq:{q.identifier} ?val }} ."""
            for q in constraint.requiredQualifiers
        )
        return self._buildViolationsQuery(
            constraint,
            inputPart,
            outerSelection,
            innerSelection,
            conditions,
        )

    def _buildAllowedQualifierConstraintViolationsQuery(
        self, constraint: AllowedQualifiersConstraint
    ) -> str:
        outerSelection = "?statement ?item ?itemLabel"
        inputPart = self._buildViolationsQueryInput(
            constraint, ViolationsQueryInputType.STATEMENT
        )
        innerSelection = "?statement"
        conditions = f"""
                    ?statement ?predicate [] .
                    [] wikibase:qualifier ?predicate .
                    FILTER(!(?predicate in ({", ".join(f"kppq:{q.identifier}" for q in constraint.allowedQualifiers)})))"""
        finalConditions = f"""
                ?item kpp:{constraint.property.identifier} ?statement ."""
        return self._buildViolationsQuery(
            constraint,
            inputPart,
            outerSelection,
            innerSelection,
            conditions,
            finalConditions=finalConditions,
        )

    def _buildConflictsWithConstraintViolationsQuery(
        self, constraint: ConflictsWithConstraint
    ) -> str:
        outerSelection = "(SAMPLE(?statement) AS ?statement) ?item ?itemLabel"
        inputPart = self._buildViolationsQueryInput(
            constraint, ViolationsQueryInputType.ITEM
        )
        innerSelection = "?item"
        conditions = f"""
                    FILTER({" ||".join(f"""
                        EXISTS {{ ?item kpt:{p.identifier} {"kp:" + v.identifier if v else "[]"} }}""" for (p,v) in constraint.conflictingStatements)
                    }
                    )"""
        finalConditions = f"""
                ?item kpp:{constraint.property.identifier} ?statement ."""
        outerGroupBy = "?item ?itemLabel"
        return self._buildViolationsQuery(
            constraint,
            inputPart,
            outerSelection,
            innerSelection,
            conditions,
            finalConditions=finalConditions,
            outerGroupBy=outerGroupBy,
        )

    def _buildDistinctValuesConstraintViolationsQuery(
        self, constraint: DistinctValuesConstraint
    ) -> str:
        outerSelection = "?statement ?item ?itemLabel ?value ?valueLabel"
        inputPart = self._buildViolationsQueryInput(
            constraint, ViolationsQueryInputType.STATEMENT_VALUE
        )
        innerSelection = "?value (COUNT(?statement) AS ?statementCount)"
        conditions = "\n".join(
            f"""
                    OPTIONAL {{ ?statement kppq:{s.identifier} ?separator{i} }} ."""
            for (i, s) in enumerate(constraint.separators)
        )
        innerGroupBy = f"?value {f" ".join(f"?separator{i}" for i in range(len(constraint.separators)))}"
        innerHaving = "?statementCount > 1"
        innerOrderBy = "?value ?statementCount"
        finalConditions = f"""
                ?statement kpps:{constraint.property.identifier} ?value .
                ?item kpp:{constraint.property.identifier} ?statement ."""
        return f"""
            # Note that the actual number of returned output rows will be
            # different from the choosen number if output is limited.
            #
            # The output limit limits the number of violating values,
            # so the actual number of output rows will be larger (at least
            # double the limit, as there must be more than 1 item for each
            # value that offends distinct-values-constraint). We could limit
            # the final part of the query instead, but this would yield no
            # speed results at all as the heavy work happens in the query
            # before it. For other constraints the final step never adds extra
            # results, which is why there the limits do match the results.\n""" + self._buildViolationsQuery(
            constraint,
            inputPart,
            outerSelection,
            innerSelection,
            conditions,
            innerGroupBy=innerGroupBy,
            innerHaving=innerHaving,
            innerOrderBy=innerOrderBy,
            finalConditions=finalConditions,
        )

    def _buildFormatConstraintViolationsQuery(
        self, constraint: FormatConstraint
    ) -> str:
        outerSelection = "?statement ?item ?itemLabel ?value"
        inputPart = self._buildViolationsQueryInput(
            constraint, ViolationsQueryInputType.STATEMENT_VALUE
        )
        innerSelection = "?statement ?value"
        conditions = f"""
                    FILTER(!REGEX(STR(?value), "{constraint.format.replace("\\", "\\\\")}"))"""
        finalConditions = f"""
                ?item kpp:{constraint.property.identifier} ?statement ."""
        return self._buildViolationsQuery(
            constraint,
            inputPart,
            outerSelection,
            innerSelection,
            conditions,
            finalConditions=finalConditions,
        )

    def _buildItemRequiresStatementConstraintViolationsQuery(
        self, constraint: ItemRequiresStatementConstraint
    ) -> str:
        outerSelection = "(SAMPLE(?statement) AS ?statement) ?item ?itemLabel"
        inputPart = self._buildViolationsQueryInput(
            constraint, ViolationsQueryInputType.ITEM
        )
        innerSelection = "?item"
        conditions = f"""
                    FILTER({" ||".join(f"""
                        NOT EXISTS {{ ?item kpt:{s[0].identifier} ?v . {f"VALUES ?v {{{" ".join("kp:" + v.identifier for v in s[1])}}}" if s[1] else ""} }}""" for s in constraint.requiredStatements.values())
                    }
                    )"""
        finalConditions = f"""
                ?item kpp:{constraint.property.identifier} ?statement ."""
        outerGroupBy = "?item ?itemLabel"
        return self._buildViolationsQuery(
            constraint,
            inputPart,
            outerSelection,
            innerSelection,
            conditions,
            finalConditions=finalConditions,
            outerGroupBy=outerGroupBy,
        )

    def _buildValueRequiresStatementConstraintViolationsQuery(
        self, constraint: ValueRequiresStatementConstraint
    ) -> str:
        outerSelection = "?statement ?item ?itemLabel ?value ?valueLabel"
        inputPart = self._buildViolationsQueryInput(
            constraint, ViolationsQueryInputType.STATEMENT_VALUE
        )
        innerSelection = "?statement ?value"
        conditions = f"""
                    FILTER({" ||".join(f"""
                        NOT EXISTS {{ ?value kpt:{s[0].identifier} ?v . {f"VALUES ?v {{{" ".join("kp:" + v.identifier for v in s[1])}}}" if s[1] else ""} }}""" for s in constraint.requiredStatements.values())
                    }
                    )"""
        finalConditions = f"""
                ?item kpp:{constraint.property.identifier} ?statement ."""
        return self._buildViolationsQuery(
            constraint,
            inputPart,
            outerSelection,
            innerSelection,
            conditions,
            finalConditions=finalConditions,
        )

    def _buildViolationsQueryInput(
        self, constraint: Constraint, inputType: ViolationsQueryInputType
    ) -> str:
        optionalDistinct = ""
        if inputType == ViolationsQueryInputType.ITEM:
            optionalDistinct = "DISTINCT "
            selection = "?item"
            condition = f"?item kpp:{constraint.property.identifier} []"
        elif inputType == ViolationsQueryInputType.ITEM_STATEMENT:
            selection = "?item ?statement"
            condition = f"?item kpp:{constraint.property.identifier} ?statement"
        elif inputType == ViolationsQueryInputType.ITEM_STATEMENT_VALUE:
            selection = "?item ?statement ?value"
            condition = f"""?item kpp:{constraint.property.identifier} ?statement .
                    ?statement kpps:{constraint.property.identifier} ?value"""
        elif inputType == ViolationsQueryInputType.STATEMENT:
            selection = "?statement"
            condition = f"[] kpp:{constraint.property.identifier} ?statement"
        elif inputType == ViolationsQueryInputType.STATEMENT_VALUE:
            selection = "?statement ?value"
            condition = f"?statement kpps:{constraint.property.identifier} ?value"

        return f"""WITH
            {{
                SELECT {optionalDistinct}{selection}
                WHERE
                {{
                    {condition}
                }}{f"""{f"""
                ORDER BY {selection}"""
                    if constraint.sort else ""
                }
                LIMIT {constraint.limit} OFFSET {constraint._offset}"""
                if constraint.validationMode == ValidationMode.LIMIT_INPUT else ""
                }
            }} AS %input"""

    def _buildViolationsQuery(
        self,
        constraint: Constraint,
        inputPart: str,
        outerSelection: str,
        innerSelection: str,
        conditions: str,
        finalConditions: str = "",
        innerGroupBy: str = "",
        outerGroupBy: str = "",
        innerHaving: str = "",
        innerOrderBy: str = "",
    ) -> str:
        return f"""
            SELECT {outerSelection}

            {inputPart}

            WITH
            {{
                SELECT {innerSelection}
                WHERE
                {{
                    INCLUDE %input{conditions}
                }}{f"""
                GROUP BY {innerGroupBy}""" if innerGroupBy else ""}{f"""
                HAVING({innerHaving})""" if innerHaving else ""}{f"""{f"""
                ORDER BY {innerOrderBy or innerSelection}"""
                    if constraint.sort else ""
                }
                LIMIT {constraint.limit} OFFSET {constraint._offset}""" 
                    if constraint.validationMode == ValidationMode.LIMIT_OUTPUT else ""
                }
            }} AS %results

            WHERE
            {{
                INCLUDE %results{finalConditions}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{self._wikibaseConfig.getDefaultLanguage()}" }}
            }}{f"""
            GROUP BY {outerGroupBy}""" if outerGroupBy else ""}"""
