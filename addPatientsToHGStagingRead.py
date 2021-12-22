import json
import os

import requests

environment = "staging"


# Read from vault chr-gateway variables CLIENT_ID and CLIENT_SECRET
# and set them as env variables (needed for token generation).
# vault-login dev-uk
# vault read -field=value secret/dev-uk/chr-gateway/CLIENT_ID
# vault read -field=value secret/dev-uk/chr-gateway/CLIENT_SECRET
# Read from staging instead, if you are using that environment


def generate_service_token():
    url = 'https://services-uk.' + environment + '.babylontech.co.uk/ai-auth/v1/internal'
    header = {'Content-Type': 'application/json'}

    client_id = "86UspdFnzvjVsmmpzbKZZayw3yP5WIzU"
    client_secret = "6KAxKvhJ3j9yG-RIPpzJvQ3zvu9xRR7jAVX5NmdU6D83BJXU7u3pia5BUBxhKeHx"
    data = {'client_id': client_id, 'client_secret': client_secret}
    r = requests.post(url, headers=header, data=json.dumps(data))
    return json.loads(r.text)['access_token']


def execute_HG_query(query):
    token = generate_service_token()
    url = 'https://services-uk.' + environment + '.babylontech.co.uk/chr/graphql'
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(query))
    return json.loads(r.text)


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


def generate_vitalsigns_query(patient_uuid):
    query_string = """query { 
  getMedicalRecord(member_uuid: \"""" + patient_uuid + """\") { 
    observation { 

      component {
        code {
            coding {
                code
                display
            }
        }
        valueQuantity {
            value
            code
        }
      }
     }  
  } 
}"""
    return {"query": query_string}


def generate_patient_query(patient_uuid):
    query_string = """query{
  getMedicalRecord(member_uuid: \"""" + patient_uuid + """\") {
    patient{
      name {
        family
        given
      }
      gender
      birthDate
    }
  }
}"""
    return {"query": query_string}


mpruuids = ['ff019c74-4794-4964-b48b-5fd8aea475af', 'b04ac91f-d5b8-4fb4-bc47-dd7302133bc0', 'ae8dfddc-783a-4409-8a37-5a0b1347990e',
            '15b961ce-0823-4d22-a294-b9cb131d2949', 'fe16798d-192e-4fdc-bb23-54f3874d8990', '47346a1f-e704-40a4-b7f1-76b0aa646f06',
            '3db0d578-69b3-4be3-9b2f-8a38ac16ac6f', 'd543f8e4-a3e2-46d3-a08f-ba078678c94c', 'c9302b29-24b9-44ee-abce-456cac718834']

query = generate_patient_query(mpruuids[6])
result = execute_HG_query(query)
print(result)
print("-----------------------------------------------------")
query = generate_reportedcondition_query(mpruuids[6])
result = execute_HG_query(query)
print(result)
print("-----------------------------------------------------")
query = generate_vitalsigns_query(mpruuids[6])
result = execute_HG_query(query)
print(result)