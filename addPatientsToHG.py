import json
import string
import random
import requests
from datetime import date, datetime
import os




# Adapted from loginDevUK.sh bash script
def generate_service_token():
    url = 'https://services-uk.dev.babylontech.co.uk/ai-auth/v1/internal'
    header = {'Content-Type': 'application/json'}

    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    client_id = "1M1m7EKIyUg6e3xdDWJQEFBt4a3F3uyE"
    client_secret = "42drt7aEQTfWLnThhsJ5woWJmYkFJwN0bmKXz38rKjGmseW3d31aavY4q7ZLMiSN"
    print(client_id)
    print(client_secret)
    data = {'client_id': client_id, 'client_secret': client_secret}
    r = requests.post(url, headers=header, data=json.dumps(data))
    print(r)
    return json.loads(r.text)['access_token']

def generate_dev_uk_token():
    randomString = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
    patient = {"email": randomString + "@example.com",
               "first_name": "Jane",
               "gender": "",
               "last_name": "Doe",
               "password": "1234_Hey_thats_the_code_on_my_luggage!",
               "profileImageURL": "",
               "region_id": 1}
    params = {"agreed_terms_and_conditions": 1, "patient": patient}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    url = "https://services-uk.dev.babylontech.co.uk/ai-auth/v1/register"
    res = requests.post(url, data=json.dumps(params), headers=headers)
    resJson = json.loads(res.text)
    return resJson['kong']['access_token']

def execute_HG_query(query):
    token = generate_dev_uk_token()
    url = 'https://services-uk.dev.babylontech.co.uk/chr/graphql'
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(query))
    return json.loads(r.text)

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
    url = "https://services-uk.dev.babylontech.co.uk/chr-test-fixtures/memberData"
    headers = {'Authorization': 'Bearer ' + generate_dev_uk_token(), 'Content-Type': 'application/json'}
    res = requests.post(url, data=json.dumps(request), headers=headers)
    resJson = json.loads(res.text)
    return resJson

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

def calculate_age(born):
    born = born.split("-")
    born = date(int(born[0]),int(born[1]),int(born[2]))
    today = date.today()
    print(today)
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def ageCheck(current_age, formula):
    if 'X>18' in formula:
        if current_age > 18:
            print("X>18")
    if '64>X>18' in formula:
        if 64 > current_age > 18:
            print("64>X>18")
    if 'X<18' in formula:
        if current_age < 18:
            print("X<18")

#ageCheck(calculate_age("1973-04-08"),"X>18")

#query = generate_patient_query("80c5c5ce-4bf5-4938-ada2-09bf9c2edcb7")
#result = execute_HG_query(query)
#print(result)
#print(result['data']['getMedicalRecord']['patient']['birthDate'])

anxietyDisorder = "e6tc_Tg7Fd"
inactive = "m8tNjSMjkK"
hypertensive = "kxvgoB1X1b"
pregnancy = "DuLdf_kaOG"
vitalSignsList = []

#Jessica Potts uuid - "fc8e6d65-d226-4137-b5bf-bb6705f905c4"



testPatients = [
[["Amel", "Turcotte", "male", "1959-03-12"],["e6tc_Tg7Fd"]], # e6tc_Tg7Fd   e744b1bc-3a97-4fd1-bf32-508c70345c32
[["Abby", "Pagac", "female", "1969-06-14"],["e6tc_Tg7Fd"]],# e6tc_Tg7Fd     c77c14a5-e31d-4686-9500-cec43c25cb6f
[["Anton", "Conner", "male", "1945-07-16"],["e6tc_Tg7Fd"]], # e6tc_Tg7Fd    0421b0f4-0adb-40ec-88b7-ff3454bb6abc
[["Almida", "Ullrich", "female", "1948-11-17"],["e6tc_Tg7Fd"]], # e6tc_Tg7Fd    fcb395ba-758f-4b64-9f10-5c55fcfbf5ac
[["Clark", "Hegmann", "male", "2005-01-16"],["e6tc_Tg7Fd"]], # e6tc_Tg7Fd       dd127585-2b48-4293-92bb-09c2df0b396f
[["Cristobal", "Batista", "female", "2006-11-14"],["e6tc_Tg7Fd"]], # e6tc_Tg7Fd
[["Damon", "Willms", "male", "1967-04-08"],["kxvgoB1X1b", "e6tc_Tg7Fd"]],  # kxvgoB1X1b + e6tc_Tg7Fd
[["Carlota", "Arenas", "female", "1987-04-16"],["kxvgoB1X1b", "e6tc_Tg7Fd"]], # kxvgoB1X1b + e6tc_Tg7Fd
[["Claudio", "Mayert", "male", "1944-08-08"],["kxvgoB1X1b", "e6tc_Tg7Fd"]], # kxvgoB1X1b + e6tc_Tg7Fd
[["Chantal", "Winterheiser", "female", "1934-12-11"],["kxvgoB1X1b", "e6tc_Tg7Fd"]], # kxvgoB1X1b + e6tc_Tg7Fd
[["Dwayne", "Renner", "male", "2007-12-12"],["kxvgoB1X1b", "e6tc_Tg7Fd"]], # kxvgoB1X1b + e6tc_Tg7Fd
[["Else", "VonRueden", "female", "2008-12-10"],["kxvgoB1X1b", "e6tc_Tg7Fd"]], # kxvgoB1X1b + e6tc_Tg7Fd
[["Holli", "Parker", "female", "1977-11-11"],["DuLdf_kaOG", "e6tc_Tg7Fd"]], # DuLdf_kaOG + e6tc_Tg7Fd
[["Joslyn", "Kunde", "female", "1981-10-10"],["DuLdf_kaOG", "e6tc_Tg7Fd"]], # DuLdf_kaOG + e6tc_Tg7Fd
[["Louisa", "Roob", "female", "2005-07-04"],["DuLdf_kaOG", "e6tc_Tg7Fd"]], # DuLdf_kaOG + e6tc_Tg7Fd
[["Leon", "Metz", "male", "1966-05-05"],["m8tNjSMjkK", "e6tc_Tg7Fd"]],  # m8tNjSMjkK + e6tc_Tg7Fd
[["Maud", "Emard", "female", "1986-05-17"],["m8tNjSMjkK", "e6tc_Tg7Fd"]], # m8tNjSMjkK + e6tc_Tg7Fd
[["Norberto", "Ferry", "male", "1943-05-05"],["m8tNjSMjkK", "e6tc_Tg7Fd"]],  # m8tNjSMjkK + e6tc_Tg7Fd
[["Meghan", "Smith", "female", "1941-05-17"],["m8tNjSMjkK", "e6tc_Tg7Fd"]], # m8tNjSMjkK + e6tc_Tg7Fd
[["Rich", "Rowe", "male", "2004-05-03"],["m8tNjSMjkK", "e6tc_Tg7Fd"]],  # m8tNjSMjkK + e6tc_Tg7Fd
[["Valerie", "Abshire", "female", "2006-02-10"],["m8tNjSMjkK", "e6tc_Tg7Fd"]], # m8tNjSMjkK + e6tc_Tg7Fd
[["Sang", "Metz", "male", "1987-03-03"],["kxvgoB1X1b"]],  # kxvgoB1X1b   2202a467-862f-4b47-82b3-7f4219b3899e
[["Sylvia", "DuBuque", "female", "1980-01-09"],["kxvgoB1X1b"]], # kxvgoB1X1b   cd30ad36-2465-4ef7-87c1-dacc3ca357ca
[["Henry", "Melgar", "male", "1949-03-04"],["kxvgoB1X1b"]],  # kxvgoB1X1b     701df74e-9877-4d9b-b036-27051aee8583
[["Tiffanie", "Reilly", "female", "1948-04-13"],["kxvgoB1X1b"]], # kxvgoB1X1b   6f46609c-6b47-46b7-b24e-8e7b335fbc49
[["Kenny", "Reinger", "male", "2004-07-02"],["kxvgoB1X1b"]],  # kxvgoB1X1b
[["Ruthe", "Borer", "female", "2004-04-07"],["kxvgoB1X1b"]], # kxvgoB1X1b  54553e16-1dc6-459e-a970-450422aea708
[["Tajuana", "Herman", "female", "1988-03-06"],["DuLdf_kaOG"]],  # DuLdf_kaOG
[["Maira", "Leannon", "female", "1978-05-06"],["DuLdf_kaOG"]], # DuLdf_kaOG
[["Aliza", "Kemmer", "female", "2005-05-05"],["DuLdf_kaOG"]]  # DuLdf_kaOG
]

# for el in testPatients:
#     uuid = create_patient(el[0][0], el[0][1], el[0][2], el[0][3])
#     print(uuid)
#     for condi in el[1]:
#         cond = add_condition_to_patient(uuid, condi)


uuid = create_patient("Sang", "Metz", "male", "1987-03-03")
print(uuid)
cond = add_condition_to_patient(uuid, "kxvgoB1X1b")
print(cond)
# cond = add_condition_to_patient(uuid, anxietyDisorder)
# print(cond)
# cond = add_blood_pressure_to_patient(uuid, 125, 85)
# print(cond)