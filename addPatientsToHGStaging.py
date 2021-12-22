import json
import string
import random
import requests

environment = 'staging'


# Adapted from loginDevUK.sh bash script
def generate_user_token():
    random_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
    patient = {"email": random_string + "@example.com",
               "first_name": "Jane",
               "gender": "",
               "last_name": "Doe",
               "password": "1234_Hey_thats_the_code_on_my_luggage!",
               "profileImageURL": "",
               "region_id": 1}
    params = {"agreed_terms_and_conditions": 1, "patient": patient}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    url = "https://services-uk." + environment + ".babylontech.co.uk/ai-auth/v1/register"
    res = requests.post(url, data=json.dumps(params), headers=headers)
    res_json = json.loads(res.text)
    return res_json['kong']['access_token']


def create_patient(first_name, last_name, gender, date_of_birth):
    patient = {"firstName": first_name, "lastName": last_name, "gender": gender, "dateOfBirth": date_of_birth}
    profile = {"profile": patient}
    resources = []
    request = {"resources": resources, "member": profile}
    result = execute_chr_test_fixture_request(request)
    return result['member']['uuid']


def add_condition_to_patient(patient_uuid, condition_code):
    member = {"uuid": patient_uuid}
    resources = [{"templateName": "ReportedCondition",
                  "topicName": "dfhir.reportedcondition.v1",
                  "fields": {"code": condition_code}}]
    request = {"member": member, "resources": resources}
    result = execute_chr_test_fixture_request(request)
    return result


def add_blood_pressure_to_patient(patient_uuid, diastolic, systolic):
    member = {"uuid": patient_uuid}
    resources = [{"templateName": "VitalSignsBloodPressure",
                  "topicName": "dfhir.vitalsigns.bloodpressure.v1",
                  "fields": {"diastolicBpValue": diastolic, "systolicBpValue": systolic}}]
    request = {"member": member, "resources": resources}
    result = execute_chr_test_fixture_request(request)
    return result


def execute_chr_test_fixture_request(request):
    url = "https://services-uk." + environment + ".babylontech.co.uk/chr-test-fixtures/memberData"
    headers = {'Authorization': 'Bearer ' + generate_user_token(), 'Content-Type': 'application/json'}
    res = requests.post(url, data=json.dumps(request), headers=headers)
    res_json = json.loads(res.text)
    return res_json


uuid = create_patient("Sang", "Metz", "male", "1987-03-03")
print(uuid)
cond = add_condition_to_patient(uuid, "kxvgoB1X1b")
print(cond)
#cond = add_condition_to_patient(uuid, "e6tc_Tg7Fd")
#print(cond)
cond = add_blood_pressure_to_patient(uuid, 120, 80)
print(cond)


# [["Sang", "Metz", "male", "1987-03-03"],["kxvgoB1X1b"]],  # kxvgoB1X1b    ff019c74-4794-4964-b48b-5fd8aea475af
# [["Sylvia", "DuBuque", "female", "1980-01-09"],["kxvgoB1X1b"]], # kxvgoB1X1b   b04ac91f-d5b8-4fb4-bc47-dd7302133bc0
# [["Henry", "Melgar", "male", "1949-03-04"],["kxvgoB1X1b"]],  # kxvgoB1X1b      ae8dfddc-783a-4409-8a37-5a0b1347990e
# [["Tiffanie", "Reilly", "female", "1948-04-13"],["kxvgoB1X1b"]], # kxvgoB1X1b   15b961ce-0823-4d22-a294-b9cb131d2949
# [["Kenny", "Reinger", "male", "2004-07-02"],["kxvgoB1X1b"]],  # kxvgoB1X1b    fe16798d-192e-4fdc-bb23-54f3874d8990
# [["Ruthe", "Borer", "female", "2004-04-07"],["kxvgoB1X1b"]], # kxvgoB1X1b   47346a1f-e704-40a4-b7f1-76b0aa646f06

#[["Leon", "Metz", "male", "1966-05-05"],["m8tNjSMjkK", "e6tc_Tg7Fd"]]    3db0d578-69b3-4be3-9b2f-8a38ac16ac6f
#[["Rich", "Rowe", "male", "2004-05-03"],["m8tNjSMjkK", "e6tc_Tg7Fd"]]     d543f8e4-a3e2-46d3-a08f-ba078678c94c
#[["Meghan", "Smith", "female", "1941-05-17"],["m8tNjSMjkK", "e6tc_Tg7Fd"]]  c9302b29-24b9-44ee-abce-456cac718834

mpruuids = ['ff019c74-4794-4964-b48b-5fd8aea475af', 'b04ac91f-d5b8-4fb4-bc47-dd7302133bc0', 'ae8dfddc-783a-4409-8a37-5a0b1347990e',
            '15b961ce-0823-4d22-a294-b9cb131d2949', 'fe16798d-192e-4fdc-bb23-54f3874d8990', '47346a1f-e704-40a4-b7f1-76b0aa646f06',
            '3db0d578-69b3-4be3-9b2f-8a38ac16ac6f', 'd543f8e4-a3e2-46d3-a08f-ba078678c94c', 'c9302b29-24b9-44ee-abce-456cac718834']