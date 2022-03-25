from tinydb import TinyDB, Query
import names
import time
import json
import string
import random
import requests
import datetime

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

#-----------------------------------------------------------------------------------------------------------------------

db = TinyDB('advisorPatientsInHG.json')
tags = ["hypertension", "low back pain", "anxiety"]
pregnant = "DuLdf_kaOG";
ACEinhibitor = "R1JSUN6GdZ";
AngiotensinIIReceptorAntagonist = "GCtYSKFyHN";
ReninInhibitor = "FNqX5CkHk"
CCB = "3q8Z5tb8e8";
CKD = "ktIvFMGdna";
Albuminuria = "PDc0HGgCeL";
Thiazide = "H3e4IoNDWi";
Diabetes = "YoTs_GRdm8";
TransplantedKidney = "HhkA8Yw9GH"
HFpEF = "xkbKx4gqZ9";
PAD = "_uvf-5g2Qm";
CerebrovascularDisease = "ay9FqhhjBP";
StableAngina = "M4vJc4NwsO";
StableIHD = "qcfZrvyxPO"
AF = "m8m9GCRTo1";
AorticAneurysm = "iD3yFxsdrP";
HeartValveDisorder = "Ror64-IDlH";

lbp = "mPLg3kYjHR"
acutelbp = "i65KN4tQQW"
chroniclbp = "ngKRMRPB4I"
acupuncture = "rabmrljdkG"
nsaids = "KOR97NFm2J"
none = "none"

def randomBlooPressure():
    sbpNormal = random.randint(90, 119); sbpElevated = random.randint(120, 129); sbpStage1 = random.randint(130, 139)
    sbpStage2 = random.randint(140, 179); sbpCrisis = random.randint(180, 200)

    dbpNormal = random.randint(60, 79); dbpElevated = random.randint(0, 79); dbpStage1 = random.randint(80, 89)
    dbpStage2 = random.randint(90, 119); dbpCrisis = random.randint(120, 140)

    sbpdbpNormal = [sbpNormal, dbpNormal]; sbpdbpElevated = [sbpElevated, dbpElevated]; sbpdbpElevated2 = [sbpElevated, dbpNormal]
    sbpdbpStage1 = [sbpStage1, dbpStage1]; sbpdbpStage1a = [sbpStage1, dbpElevated]; sbpdbpStage1b = [sbpStage1, dbpNormal]
    sbpdbpStage1c = [sbpElevated, dbpStage1]; sbpdbpStage1d = [sbpNormal, dbpStage1]; sbpdbpStage2 = [sbpStage2, dbpStage2]
    sbpdbpStage2a = [sbpStage2, dbpElevated]; sbpdbpStage2b = [sbpStage2, dbpNormal]; sbpdbpStage2c = [sbpElevated, dbpStage2]
    sbpdbpStage2d = [sbpNormal, dbpStage2]; sbpdbpStage2e = [sbpStage2, dbpStage1]; sbpdbpStage2f = [sbpStage1, dbpStage2]
    sbpdbpCrisis = [sbpCrisis, dbpCrisis]; sbpdbpCrisis1 = [sbpCrisis, dbpStage2]; sbpdbpCrisis2 = [sbpStage2, dbpCrisis]

    sbpdbp = [sbpdbpNormal, sbpdbpElevated, sbpdbpElevated2, sbpdbpStage1, sbpdbpStage1a, sbpdbpStage1b, sbpdbpStage1c, sbpdbpStage1d,
              sbpdbpStage2, sbpdbpStage2a, sbpdbpStage2b, sbpdbpStage2c, sbpdbpStage2d, sbpdbpStage2e, sbpdbpStage2f,
              sbpdbpCrisis, sbpdbpCrisis1, sbpdbpCrisis2]

    randomSbpDbp = random.choice(sbpdbp)
    return randomSbpDbp


def str_time_prop(start, end, time_format, prop):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))

def random_dateUndeer18():
    start = "2005-1-1"
    end = "2022-1-1"
    prop = random.random()
    return str_time_prop(start, end, '%Y-%m-%d', prop)

def random_dateAdult():
    start = "1958-1-1"
    end = "2004-1-1"
    prop = random.random()
    return str_time_prop(start, end, '%Y-%m-%d', prop)

def random_dateOldAge():
    start = "1925-1-1"
    end = "1958-1-1"
    prop = random.random()
    return str_time_prop(start, end, '%Y-%m-%d', prop)

def randomDOB():
    under18 = random_dateUndeer18()
    adult = random_dateAdult()
    oldAge = random_dateOldAge()
    dob = [under18, adult, oldAge]
    randomDob = random.choice(dob)
    return randomDob

def randomGend():
    gender = ["male", "female"]
    randomGender = random.choice(gender)
    return randomGender

def randomCond():
    conditionHypertension = [pregnant, CKD, Albuminuria, Diabetes, TransplantedKidney, HFpEF, PAD, CerebrovascularDisease,
                             StableAngina, StableIHD, AF, AorticAneurysm, HeartValveDisorder, none, none, none, none, none,
                             none, none, none, none, none, none, none, none, none, none, none, none, none, none, none]
    therapyHypertension = [ACEinhibitor, AngiotensinIIReceptorAntagonist, ReninInhibitor, CCB, Thiazide]
    conditionsLowBackPain = [lbp, chroniclbp]
    therapyLBP = [acupuncture, nsaids]
    randomCondition = random.choice(conditionHypertension)
    return randomCondition

def randomizeData():
    randomGender = randomGend()
    randomDob = randomDOB()
    randomCondition = randomCond()
    randomSbpDbp = randomBlooPressure()

    return randomGender, randomDob, randomCondition, randomSbpDbp


def printAll():
    for el in db.all():
        print(el)

def printMemberByUuid(uuid):
    User = Query()
    print(db.search(User.uuid == uuid))

def printMembersByVersion(version):
    User = Query()
    print(db.search(User.version == version))

def removeMembersByVersion(version):
    User = Query()
    db.remove(User.version == version)

def updateUUIDinTinyDB(uuid, name, surname):
    User = Query()
    db.update({'uuid': uuid}, (User.name == name and User.surname == surname))

def addPatientToHG(patient):
    uuid = create_patient(patient['name'], patient['surname'], patient['sex'], patient['dob'])
    print(uuid)
    updateUUIDinTinyDB(uuid, patient['name'], patient['surname'] )
    if patient['conditions'][0]!= "none":
        for cond in patient['conditions']:
            process_output(add_condition_to_patient(uuid, cond, present=True))
    if patient['BP'][0]!="none":
        process_output(add_blood_pressure_to_patient(uuid, patient['BP'][0], patient['BP'][1]))
    return uuid

def addPatientToTinyDB(randomGender, randomDob, randomCondition, randomSbpDbp, tag, version):
    patient = {
            "name": names.get_first_name(gender = randomGender),
            "surname": names.get_last_name(),
            "dob": randomDob,
            "sex": randomGender,
            "conditions": randomCondition,
            "BP": randomSbpDbp,
            "uuid": "",
            "tag": tag,
            "version": version
    }
    print(patient)
    #db.insert(patient)

def addNMembersToTinyDB(num):
    for x in range(num):
        randomGender, randomDob, randomCondition, randomSbpDbp = randomizeData()
        if (randomGender == "male" and randomCondition == pregnant) == False:
            addPatientToTinyDB(randomGender, randomDob, randomCondition, randomSbpDbp, "hypertension", "experiment1")

#removeMembersByVersion("experiment1")
#printMembersByVersion("experiment1")
printAll()
print("--------------")

User = Query()
print(db.search(User.name == "Andrew" and User.surname == "Topps"))