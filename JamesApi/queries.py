from typing import Dict, List
from gql import gql
import json
import requests
from rdflib import URIRef
from rdf_uris import (
    PROPERTY_URIS
)


# HG_PATIENT_INFO_QUERY = gql(
#     """
#     query($patient_uuid: ID!) {
#       getMedicalRecord(member_uuid: $patient_uuid) {
#         patient {
#           id
#           birthDate
#           sexAtBirth {
#             system
#             code
#             display
#           }
#         }
#       }
#     }
#     """
# )

def generate_reportedcondition_query(patient_uuid):
    query_string = """query {
            getMedicalRecord(member_uuid: \"""" + patient_uuid + """\") {
              condition {
                id
                code{
                  coding{
                    system
                    code
                    display
                  }
                }
                verificationStatus {
                  coding{
                    system
                    code
                    display
                  }
                }
          convertedCode {
            display
            system
            }
          }
      }
    }"""
    return {"query": query_string}

def get_patient_info(patient_uuid, token):
    url = 'https://services-uk.dev.babylontech.co.uk/chr/graphql'
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(generate_reportedcondition_query(patient_uuid)))
    return json.loads(r.text)

# def get_patient_info(patient_uuid, hg_client):
#     result = hg_client.execute(
#         HG_PATIENT_INFO_QUERY,
#         variable_values={
#             "patient_uuid": patient_uuid,
#         },
#     )
#     return result["getMedicalRecord"]["patient"]


HG_CODES_QUERY = gql(
    """
    query($patient_uuid: ID!, $codes: [CodeFilterOption]) {
      getMedicalRecord(member_uuid: $patient_uuid) {
        condition(
          search: {
            code: { oneOf: $codes }
          }
        ) {
          id
          code {
            coding {
              system
              code
              display
            }
          }
          verificationStatus {
            coding {
              system
              code
              display
            }
          }
          convertedCode {
            display
            system
          }
        }
      }
    }
    """
)


def parse_hg_codes(hg_response: Dict) -> List[str]:
    conditions = hg_response["getMedicalRecord"]["condition"]
    code_uris = [
        f"{code['system']}/{code['code']}"
        for condition in conditions
        for code in condition["code"]["coding"]
    ]
    return code_uris


def get_bbln_codes_for_patient(patient_uuid, bbln_codes, hg_client):
    return parse_hg_codes(
        hg_client.execute(
            HG_CODES_QUERY,
            variable_values={
                "patient_uuid": patient_uuid,
                "codes": bbln_codes,
            },
        )
    )


def all_actions_query(url):
    return (
        f"SELECT ?x\n"
        f"WHERE {{\n"
        f"?x rdfs:subClassOf <"+str(url)+"> .\n"
        "}"
    )


def next_action_query(action_uri: URIRef):
    return (
        f"SELECT ?x ?o\n"
        f"WHERE {{\n"
        f"  <{action_uri}> rdfs:subClassOf ?x .\n"
        f"  ?x rdf:type owl:Restriction .\n"
        f"  ?x owl:onProperty <{PROPERTY_URIS['next']}> .\n"
        f"  ?x owl:someValuesFrom ?o .\n"
        f"}}"
    )


def action_requirements_query(action_uri: URIRef):
    return (
        f"SELECT ?x ?o\n"
        f"WHERE {{\n"
        f"  <{action_uri}> rdfs:subClassOf ?x .\n"
        f"  ?x rdf:type owl:Restriction .\n"
        f"  ?x owl:onProperty <{PROPERTY_URIS['has_requirement']}> .\n"
        f"  ?x owl:someValuesFrom ?o .\n"
        f"}}"
    )


def action_age_requirement_query(action_uri: URIRef):
    return (
        f"SELECT ?x ?o\n"
        f"WHERE {{\n"
        f"  <{action_uri}> rdfs:subClassOf ?x .\n"
        f"  ?x rdf:type owl:Restriction .\n"
        f"  ?x owl:onProperty <{PROPERTY_URIS['has_age_requirement']}> .\n"
        f"  ?x owl:someValuesFrom ?o .\n"
        f"}}"
    )


def first_action_query(process_uri: URIRef):
    return (
        f"SELECT ?x ?o\n"
        f"WHERE {{\n"
        f"  <{process_uri}> rdfs:subClassOf ?x .\n"
        f"  ?x rdf:type owl:Restriction .\n"
        f"  ?x owl:onProperty <{PROPERTY_URIS['first']}> .\n"
        f"  ?x owl:someValuesFrom ?o .\n"
        f"}}"
    )


def all_processes_query(url):
    return (
        f"SELECT ?x\n"
        f"WHERE {{\n"
        f"?x rdfs:subClassOf <"+str(url)+"> .\n"
        f"}}"
    )


def next_process_query(process_uri: URIRef):
    return (
        f"SELECT ?x ?o\n"
        f"WHERE {{\n"
        f"  <{process_uri}> rdfs:subClassOf ?x .\n"
        f"  ?x rdf:type owl:Restriction .\n"
        f"  ?x owl:onProperty <{PROPERTY_URIS['next']}> .\n"
        f"  ?x owl:someValuesFrom ?o .\n"
        f"}}"
    )
