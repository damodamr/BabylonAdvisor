
# Based on https://github.com/babylonhealth/babylon-advisor-prototype/blob/master/SamplePatients.py

import json
import string
import random
import requests
import datetime
import time

environment = 'dev'


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


def add_condition_to_patient(patient_uuid, condition_code, present=True):
    assert present in [True, False, 'NOT_SURE']

    fields = {"code": condition_code}
    if present is False:
        fields["negation"] = {"negationType": "REPORTED_CONDITION_NEGATION_TYPE_FALSE"}
    elif present == "NOT_SURE":
        fields["negation"] = {"negationType": "REPORTED_CONDITION_NEGATION_TYPE_NOT_SURE"}
    else:
        # Why is it necessary?
        fields["negation"] = None

    fields["verificationStatus"] = "REPORTED_CONDITION_VERIFICATION_STATUS_CONFIRMED"

    member = {"uuid": patient_uuid}
    resources = [{"templateName": "ReportedCondition",
                  "topicName": "dfhir.reportedcondition.v1",
                  "fields": fields}]
    request = {"member": member, "resources": resources}
    result = execute_chr_test_fixture_request(request)
    return result


def get_current_time():
    # https://stackoverflow.com/questions/19654578/python-utc-datetime-objects-iso-format-doesnt-include-z-zulu-or-zero-offset
    # https://stackoverflow.com/questions/7588511/format-a-datetime-into-a-string-with-milliseconds
    # TODO: improve:
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"


def add_blood_pressure_to_patient(patient_uuid, systolic, diastolic):
    current_time = get_current_time()

    member = {"uuid": patient_uuid}
    resources = [{"templateName": "VitalSignsBloodPressure",
                  "topicName": "dfhir.vitalsigns.bloodpressure.v1",
                  "fields": {"diastolicBpValue": diastolic, "systolicBpValue": systolic, "effectiveDateTime": current_time}}]
    request = {"member": member, "resources": resources}
    result = execute_chr_test_fixture_request(request)
    return result


def add_vital_sign_body_measurement_to_patient(patient_uuid, vital_sign_body_measurement_type, value):
    effective_date_time = get_current_time()

    # TODO: check the 'topicName'

    fields = {}
    fields['effectiveDateTime'] = effective_date_time
    fields['value'] = value
    fields['type'] = vital_sign_body_measurement_type

    member = {"uuid": patient_uuid}
    resources = [{"templateName": "VitalSignsBodyMeasurement",
                  "topicName": "dfhir.vitalsigns.bodymeasurement.v1",
                  "fields": fields}]
    request = {"member": member, "resources": resources}
    result = execute_chr_test_fixture_request(request)
    return result


def execute_chr_test_fixture_request(request):
    url = "https://services-uk." + environment + ".babylontech.co.uk/chr-test-fixtures/memberData"
    headers = {'Authorization': 'Bearer ' + generate_user_token(), 'Content-Type': 'application/json'}
    res = requests.post(url, data=json.dumps(request), headers=headers)
    res_json = json.loads(res.text)
    return res_json


def process_output(output):
    if 'error' in output:
        print("!!! Error")
    else:
        print("Success (?)") # ??? # TODO: to check!

#------ADD INSIGHT CARD TO HG ------------------------------------------------------------------------------------------

def addBAinsightCard(patient_uuid, reasonReferenceID, action):
    instantiatesUri = {"instantiatesUri": "http://webprotege.stanford.edu/RtPIt3Juu0hYK529Kvo4RL"}
    id = {"id": "c45d94ef-f2a7-46c3-b737-4f0a9d0f3203"+action['uri']} #this is done by specific library
    subject = {"subject": patient_uuid}
    status = {"status": "active"}
    authoredOn = {"authoredOn": "2022-03-08T14:20:39.283Z"}
    dataRequirement = {"dataRequirements": {}} # same as for reson code
    reasonCode = {"reasonCode": {[{"code": action['requirements'][0]}, {"code": action['requirements'][1]}, {"code": action['requirements'][2]}]}}
    reasonReference = {"reasonReference": {[{"reasonReferenceId": reasonReferenceID, "reasonReferenceType": "ADVISOR_REASON_REFERENCE_TYPE_OBSERVATION" }]}}
    action = {"action": {"code": action['uri'], "display": action['label'], "advisorCommunicationRequest": {"status": "active"}}}



    member = {"uuid": patient_uuid}
    resources = [{"templateName": "AdvisorRequestGroup",
                  "topicName": "****TBD****",
                  "fields": {instantiatesUri, id, subject, status, authoredOn, dataRequirement, reasonCode, reasonReference, action}}]
    request = {"member": member, "resources": resources}
    result = execute_chr_test_fixture_request(request)

insightPatient = {
    "name": "Agatha",
    "surname": "Sith",
    "dob": "1971-05-11",
    "sex": "female",
    "conditions": ["none"],
    "BP": ["127", "78"],
    "uuid": "c45d94ef-f2a7-46c3-b737-4f0a9d0f3203"
}
action = {
    "uri" : "R833A5YFzM62nXrC72EAfED",
    "label": "Elevated BP (Prehypertensive) Pathway",
    "requirements" : ["RCutN9mVQYl6xeT57Z2cC6F",
                      "RBLZ82Kioaw4EujrQH6mqOh",
                      "RurbbbFGNgzkds7rnUGDuZ"],
    "snippet": """Recheck BP within 3 to 6 months.
                BP should be categorised as Normal, Elevated, Stage 1 or 2 Hypertension according to ranges and should be confirmed 
                with ABPM as gold standard if this is safe to do in the individual situation. Guidelines recommend use of BP averages 
                of ≥2 readings obtained on ≥2 occasions ABPM (or HBPM) used to establish a diagnosis (classification) of true 
                hypertension or white coat/masked hypertension.
                Office BP >=130/80 but <160/100 ---after 3 months of lifestyle modification---> Perform ABPM/HBPM
                = Daytime ABPM/HBPM <130/80 = White Coat (Annual ABPM/HBPM for progression + Lifestyle Modification)
                = Daytime ABPM/HBPM >=130/80 = Hypertension (Cont lifestyle modification + start antihypertensive).
                Office BP 120-129/<80 ---after 3 months of lifestyle modification---> Perform ABPM/HBPM
                = Daytime ABPM/HBPM <130/80 = Elevated BP (Annual ABPM/HBPM for progression/masked + Lifestyle Modification)
                = Daytime ABPM/HBPM >=130/80 = Masked (Cont lifestyle modification + start antihypertensive)""",
    "next": "RDEmI3taAgwiu1djPjpTgGO"
}
#ba240959-ecc9-4dc1-9e34-6a2b34fcdefc    = reason reference for blood pressure readings sbp and dbp
#hypertension uri: http://webprotege.stanford.edu/RtPIt3Juu0hYK529Kvo4RL

#addBAinsightCard()



# https://github.com/babylonhealth/schema-registry/tree/master/catalog/dfhir  - fhir catalog
# CONDITIONS = {
#     "PREGNANCY": "RS5PC-zIr8",
#     "HYPERTENSION": "kxvgoB1X1b",
#     "CKD": "ktIvFMGdna",
#     "T2DIABETES": "YoTs_GRdm8"
# }


# patients taken from spreedsheet: https://docs.google.com/spreadsheets/d/1VY1W6nbuGS67qHfMl-9tL5fYx9IcloxnG-pWQ1srFc8/edit#gid=0
patientsAdded = {
    "name" : "Andrew",
    "surname" : "Topps",
    "dob": "1984-06-12",
    "sex":"male",
    "conditions": ["none"],
    "BP" : ["117","78"],
    "uuid" : "86eec303-2c86-4e43-bde7-d4d8c74bdb37"
},{
    "name" : "Agatha",
    "surname" : "Sith",
    "dob": "1971-05-11",
    "sex":"female",
    "conditions": ["none"],
    "BP" : ["127","78"],
    "uuid" : "c45d94ef-f2a7-46c3-b737-4f0a9d0f3203"
},{
    "name" : "Anna",
    "surname" : "Becker",
    "dob": "1968-04-14",
    "sex":"female",
    "conditions": ["none"],
    "BP" : ["135","80"],
    "uuid" : "ed36394f-dbd5-4d6b-9023-8bb533b30391"
}, {
    "name" : "Andrea",
    "surname" : "Carson",
    "dob": "1968-04-19",
    "sex":"female",
    "conditions": ["none"],
    "BP" : ["120","87"],
    "uuid" : "f70ecf0e-73c7-4721-b467-0c442834ddb9"
},{
    "name" : "Beth",
    "surname" : "Dalston",
    "dob": "1974-03-10",
    "sex":"female",
    "conditions": ["none"],
    "BP" : ["135","87"],
    "uuid" : "17163ebc-1967-48e7-aefd-2d8d5fa8e3d9"
}, {
    "name" : "Andrea",
    "surname" : "Carbuncle",
    "dob": "1965-08-10",
    "sex":"female",
    "conditions": ["none"],
    "BP" : ["135","80"],
    "uuid" : "46f00d49-7cd7-41a1-b314-f651c8e25d59"
}, {
    "name" : "Anita",
    "surname" : "Sotz",
    "dob": "1966-04-03",
    "sex":"female",
    "conditions": ["none"],
    "BP" : ["136","87"],
    "uuid" : "bf624497-c219-4763-9f60-ea164124a62e"
}, {
    "name": "Brian",
    "surname": "Sotz",
    "dob": "1968-03-01",
    "sex": "male",
    "conditions": ["none"],
    "BP": ["135", "87"],
    "uuid": "d30b6126-a7bc-4098-a05a-2a450deeeeaf"
}, {
    "name": "Lara",
    "surname": "Swanson",
    "dob": "1968-02-02",
    "sex": "female",
    "conditions": ["none"],
    "BP": ["155", "80"],
    "uuid": "45beb128-845c-4249-af6f-686fe9ce7988"
}, {
    "name": "Laura",
    "surname": "Anson",
    "dob": "1968-01-18",
    "sex": "female",
    "conditions": ["none"],
    "BP": ["155", "92"],
    "uuid": "9c19b463-ca95-4a5d-9483-479320e7a292"
}, {
    "name": "Tara",
    "surname": "Goop",
    "dob": "1968-12-12",
    "sex": "female",
    "conditions": ["none"],
    "BP": ["185", "92"],
    "uuid": "53051c4c-db6e-44c0-a92d-51de2e033d44"
}, {
    "name": "Sara",
    "surname": "Mckenzie",
    "dob": "1968-11-09",
    "sex": "female",
    "conditions": ["BPoQa9GGfW", "5bpmveKEtF"],
    "BP": ["155", "125"],
    "uuid": "9e4f946d-d5c1-450f-af37-4a8cabac7769"
}, {
    "name": "Anita",
    "surname": "Gilespie",
    "dob": "1968-04-06",
    "sex": "female",
    "conditions": ["none"],
    "BP": ["185", "125"],
    "uuid": "57c382f7-fce1-45b0-a520-9326335e0fbe"
} , {
    "name": "Guy",
    "surname": "Thalys",
    "dob": "1996-05-05",
    "sex": "male",
    "conditions": ["mPLg3kYjHR"],
    "BP": ["none"],
    "uuid": "ef91f81a-b86d-4e0b-bc80-5ba67fab511d"
}

patients = {
    "name": "Amanda", #Pregnant Patient
    "surname": "Spring",
    "dob": "1989-06-05",
    "sex": "female",
    "conditions": ["DuLdf_kaOG"],
    "BP": ["145", "98"],
    "uuid": "2d86f8aa-4494-445b-9b7d-4c3e47781be7"
},{
    "name": "Ed", #Older Aged Patient
    "surname": "Coulson",
    "dob": "1955-04-05",
    "sex": "male",
    "conditions": ["none"],
    "BP": ["147", "88"],
    "uuid": "f6764973-fc1b-4a04-89aa-7f929ff703e6"
}, {
    "name": "Edna",   #CKD Patient 2
    "surname": "Coulson",
    "dob": "1961-07-07",
    "sex": "female",
    "conditions": ["ktIvFMGdna", "PDc0HGgCeL"],
    "BP": ["135", "90"],
    "uuid": "445f8eb4-da5f-42c2-9be9-1d2c270a7014"
}, {
    "name": "Tamara",   #CKD Patient 3
    "surname": "Kwart",
    "dob": "1968-08-08",
    "sex": "female",
    "conditions": ["ktIvFMGdna"],
    "BP": ["125", "78"],
    "uuid": "754a9a21-c88d-4f5a-b7ef-98ed0e380173"
} ,{
    "name": "Tam",  # DM Patient 1
    "surname": "Pam",
    "dob": "1968-08-08",
    "sex": "male",
    "conditions": ["YoTs_GRdm8"],
    "BP": ["129", "77"],
    "uuid": ""
}

"""
"Renal Transplant Patient 1
Age: 51
Sex: Female
Conditions: Transplanted Kidney
BP = 145/91"	
	
"HFpEF Patient 1
Age: 54
Sex: Male
Conditions: HFpEF
BP = 129/77"	

"PAD Patient 1
Age: 54
Sex: Male
Conditions: PAD
BP = 129/77"	

"Secondary Stroke Prevention Patient 2
Age: 54
Sex: Female
Conditions: Stroke
BP = 155/83"	
	
	
	
	
	
"Pregnant Patient
Age: 33
Sex: Female
Conditions: None
BP = 125/77
ACEi (Rampiril 2.5mg)"	

	
"CKD Patient 1
Age: 64
Sex: Female
Conditions: CKD, Stage 1
BP = 145/98
Albuminuria not present
CCB (Amlodipine 5mg)"	

"CKD Patient 4
Age: 54
Sex: Femle
Conditions: CKD, Stage 3
BP = 128/78
ARB (Losartan 100mg OD) + 
Chlorthalidone  25mg OM)"	
	
	

"Patient 2
Age:
Sex:
Conditions: LBP  
<3 months, No serious consition"

"Patient 3
Age:43
Sex: Female
Conditions: LBP  
<3 months, 
serious condition found"

"Patient 4
Age: 32
Sex: Female
Condition: LBP  
<3 months, 
No serious condition. Pain not resolved. 
Therapy Skeletal muscle relaxant
Functional deficit"

"Age: 32 Sex: Female 
Condition: LBP > 3 months, 
No serious condition. 
Therapy CBT,

"Age: 56 Sex: Male 
Condition: LBP > 3 months, 
No serious condition. 
Therapy Spinal manipulation, 
Pain not resolved. NO Functional deficit
Serious condition found later"

"Age: 26 Sex: Male Condition: LBP < 3 months, 
No serious condition. 
Therapy Antidepressants, 
Pain not resolved. NO Functional deficit 
NO Serious condition found later"

--------

"Patient 5B
Age: 56
Sex: Femle
Conditions: no conditions
BP = 135/92
Allergy to ACEi"	
	
	
"Patient 6C
Age: 54
Sex: Femle
Conditions: no conditions
BP = 185/125
no end organ damage
ACEi not tolerated due to cough"	
"""
def addPatient(patient):
    uuid = create_patient(patient['name'], patient['surname'], patient['sex'], patient['dob'])
    print(uuid)
    if patient['conditions'][0]!= "none":
        for cond in patient['conditions']:
            process_output(add_condition_to_patient(uuid, cond, present=True))
    if patient['BP'][0]!="none":
        process_output(add_blood_pressure_to_patient(uuid, patient['BP'][0], patient['BP'][1]))

for patient in patients:
    addPatient(patient)

#process_output(add_condition_to_patient("2d86f8aa-4494-445b-9b7d-4c3e47781be7","DuLdf_kaOG",present=True))