import json
from looker_sdk import client, models, error


# client calls will now automatically authenticate using the
# api3credentials specified in 'looker.ini'
sdk = client.setup("looker.ini")
looker_api_user = sdk.me()


def update_and_run_query(query_id, changes):
    # Get old query
    old_query = sdk.query(query_id)
    # Make new query
    new_query = update_query_filters(old_query, changes)
    # create a new query in looker with the new filter
    new_api_query = sdk.create_query(new_query)
    # get the new query ID
    new_query_id = new_api_query.id

    # Returns JSON data
    return sdk.run_query(new_query_id, "json")


def update_query_filters(api_query, changes):
    # Get the JSON version of the query
    query = api_query.__dict__

    # In order to create a new query, read_only fields need to be removed
    # Filter config also needs to be removed otherwise it will override the filter options in the ui
    read_only_fields = [
        "id",
        "client_id",
        "slug",
        "share_url",
        "url",
        "expanded_share_url",
        "has_table_calculations",
        "can",
        "filter_config",
    ]

    for field in read_only_fields:
        if field in query:
            query.pop(field)

    # Extract the filters from the query
    filters = query["filters"]
    # the parameter 'changes' is a dictionary of keys: new_values so we update the filters dictionary
    filters.update(changes)
    # Update the query dictionary with the new filters
    query.update({"filters": filters})

    # Returns a JSON object ready to create a new query
    return query


def update_look_filters(look_id, changes):
    # get look
    look = sdk.look(look_id)

    # get query from look
    old_query = look.query

    # change filters, get a JSON new_query in the process
    new_query = update_query_filters(old_query, changes)

    # create a new query in looker with the new filter
    new_api_query = sdk.create_query(new_query)

    # To modify the look's filters, we just need to pass the new query id
    new_query_id = new_api_query.id

    # update the look
    updatedlook = sdk.update_look(look_id, {"query_id": new_query_id})

    # returns a JSON object of the updated look, in case we need that
    # The important thing is that the look has been updated in our looker instance
    return updatedlook.__dict__


def run_look(look_id):
    return sdk.run_look(look_id, "json")


def fix_dictionary_keys(dictionary):
    # Change column names: replace . with _ so it doesn't interfere with dictionary key.value notation
    fixed_dictionary = {}
    for key, value in dictionary.items():
        new_key = key.replace(".", "_")
        fixed_dictionary[new_key] = value
    return fixed_dictionary
