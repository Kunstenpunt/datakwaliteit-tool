import re


def query_result_to_list(query_result):
    # First row is the header
    variable_names = query_result["head"]["vars"]
    result = [variable_names]
    # Next come the value rows
    for query_row in query_result["results"]["bindings"]:
        result_row = []
        for variable_name in variable_names:
            result_row.append(
                query_row[variable_name]["value"]
                if variable_name in query_row
                else None
            )
        result.append(result_row)
    return result


def strip_url_part(url):
    return url.rsplit("/", 1)[-1]


def url_from_id(possible_id, base_url):
    property_regex = re.compile(r"^P\d+$")
    entity_regex = re.compile(r"^Q\d+$")
    if property_regex.match(possible_id) or entity_regex.match(possible_id):
        return f"{base_url}/entity/{possible_id}"
    else:
        return None
