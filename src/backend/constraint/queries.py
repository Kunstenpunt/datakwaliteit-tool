from typing import Optional

from .base import Constraint, ValidationInputCountType
from .constraint_types import *
from ..wikibasehelper import WikibaseConfig


class QueryBuilder:

    def __init__(self, wikibaseConfig: WikibaseConfig):
        self._wikibaseConfig = wikibaseConfig

    def buildInputCountQuery(self, constraint: Constraint) -> Optional[str]:
        countType = constraint.validationInputCountType
        if countType == ValidationInputCountType.STATEMENTS:
            return f"""
                SELECT (COUNT(*) as ?count)
                WHERE
                {{
                    ?entity kpp:{constraint.property.identifier} ?statement
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
                    BIND (IRI(replace(str(?classQualifier), str(kppq:), str(kp:)))  AS ?classQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
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
                        bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                        ?relationQualifierEntity rdfs:label ?relationQualifierLabel .
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
                BIND (IRI(replace(str(?formatQualifier), str(kppq:), str(kp:)))  AS ?formatQualifierEntity) .
                SERVICE wikibase:label
                {{
                    bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                    ?formatQualifierEntity rdfs:label ?formatQualifierLabel .
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
                    BIND (IRI(replace(str(?propertyQualifier), str(kppq:), str(kp:)))  AS ?propertyQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                        ?propertyQualifierEntity rdfs:label ?propertyQualifierLabel .
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
                    BIND (IRI(replace(str(?propertyQualifier), str(kppq:), str(kp:)))  AS ?propertyQualifierEntity) .
                    SERVICE wikibase:label
                    {{
                        bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
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
                        bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                        ?valueQualifierEntity rdfs:label ?valueQualifierLabel .
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
                BIND (IRI(replace(str(?qualifier), str(kppq:), str(kp:)))  AS ?qualifierEntity)
                SERVICE wikibase:label
                {{
                    bd:serviceParam wikibase:language "en,{self._wikibaseConfig.getDefaultLanguage()}".
                    ?qualifierEntity rdfs:label ?qualifierLabel .
                }}
                FILTER (str(?qualifierLabel) = "separator")
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{ self._wikibaseConfig.getDefaultLanguage() }" . }}
            }}
        """

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
