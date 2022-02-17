from datetime import date
import json
import requests
from flask import request
from typing import Dict
from rdflib import URIRef, RDFS
from gql import Client
#from gql.transport.aiohttp import AIOHTTPTransport

from app import query_graph, rdf_graph
from enviroment import AUTH_URL, CLIENT_ID, CLIENT_SECRET, HEALTHGRAPH_URL
from queries import first_action_query
from rdf_uris import PROPERTY_URIS


def check_age_requirement(current_age: int, age_requirement: str) -> bool:
    # Age requirement checking could be done
    # far more nicely than this if statement.
    # But this is sufficient for a proof-of-concept.
    if "X>18" in age_requirement:
        return current_age > 18

    if "64>X>18" in age_requirement:
        return 64 > current_age > 18

    if "X<18" in age_requirement:
        return current_age < 18

    raise ValueError("Age requirement", age_requirement, "is not currently supported")


def dob_to_age(dob: str) -> int:
    """
    Simple utility function that converts HG date of birth into how old the person is
    """
    dob = dob.split("-")
    dob = date(int(dob[0]), int(dob[1]), int(dob[2]))
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def bbln_codes_from_requirements(requirements):
    # Get babylon codes from requirements list.
    bbln_codes = [r.get("babylon_code") for r in requirements]
    # (remove requirements that do not have a defined babylon code; these cannot be matched)
    bbln_codes = list(filter(None, bbln_codes))
    return bbln_codes


def get_first_actions_in_process(process_uri):
    #print(process_uri)
    #process_uri = get_current_process_uri()
    rows = query_graph(first_action_query(process_uri))
    return [action_from_uri(row.o) for row in rows]


def get_hg_client():
    # NOTE: For this prototype, we generate a auth token for querying the
    # healthgraph *every time* this method is called, for simplicity sake.
    # However, this is a fairly inefficient way of generating auth tokens. A
    # better solution would be to auto-refresh the token on expiry and keep it
    # cached in the application's broader context.
    auth_token = generate_service_token()
    return Client(
        transport=AIOHTTPTransport(
            url=HEALTHGRAPH_URL,
            headers={"Authorization": f"Bearer {auth_token}"},
        ),
        fetch_schema_from_transport=True,
    )



# def generate_service_token():
#     response = requests.post(
#         AUTH_URL,
#         headers={"Content-Type": "application/json"},
#         data=json.dumps({"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}),
#     )
#     token = response.json().get("access_token")
#     assert token is not None, "Access Token was not generated properly"
#     return token


def generate_service_token():
    environment = "dev"
    url = 'https://auth.global1.' + environment + '.babylontech.co.uk/oauth/token'
    header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    client_id = "1M1m7EKIyUg6e3xdDWJQEFBt4a3F3uyE"
    client_secret = "42drt7aEQTfWLnThhsJ5woWJmYkFJwN0bmKXz38rKjGmseW3d31aavY4q7ZLMiSN"
    data = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'client_credentials',
            'audience': 'https://babylonhealth.com'}
    r = requests.post(url, headers=header, data=json.dumps(data))
    return json.loads(r.text)['access_token']

def get_current_action_uri():
    json = request.get_json()
    action_uri = URIRef(json.get("action_uri", None))
    if action_uri is None:
        raise ValueError(
            "Must send a current action in the body to get the next action"
        )
    return action_uri


def get_current_process_uri():
    json = request.get_json()
    process_uri = URIRef(json.get("process_uri", None))
    if process_uri is None:
        raise ValueError(
            "Must send a current process in the body to get the next process"
        )

    return process_uri


def age_requirement_from_uri(uri: URIRef) -> Dict:
    return {"uri": uri, "label": rdf_graph.value(uri, RDFS.label)}


def finding_from_uri(uri: URIRef) -> Dict:
    return {
        "uri": uri,
        "label": rdf_graph.value(uri, RDFS.label),
        "babylon_code": {
            # All babylon codes are hosted here, so safe to hardcode during prototype.
            "system": "https://bbl.health",
            "code": rdf_graph.value(uri, PROPERTY_URIS["babylon_code"]),
        },
        "snomed": rdf_graph.value(uri, PROPERTY_URIS["snomed"]),
    }


# Can better type the response here.
def action_from_uri(uri: URIRef) -> Dict:
    return {
        "uri": uri,
        "label": rdf_graph.value(uri, RDFS.label),
        "hasSnippet": rdf_graph.value(uri, URIRef("http://webprotege.stanford.edu/R9DtWPVELKDzTWPxZMDPCZb")),
        "hasPatientFacingSnippet": rdf_graph.value(uri, URIRef("http://webprotege.stanford.edu/RDwvT4cunWbgpfEPbNE9Fz0")),
    }


def process_from_uri(uri: URIRef) -> Dict:
    return {
        "uri": uri,
        "label": rdf_graph.value(uri, RDFS.label),
        "isDefinedBy": rdf_graph.value(uri, RDFS.isDefinedBy),
    }
