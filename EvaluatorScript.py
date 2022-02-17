from pprint import pprint
import requests
import json
expressions = [
        'AGE > 18 AND SEX = "FEMALE" AND (RAG_STATUS("Blood Pressure") = RED OR REP_COND("RS5PC-zIr8"))',
        'DUMMY_HEALTHIQ() > 0.3',
        'DUMMY_HEALTHIQ() < 0.3',
        'DUMMY_RISK_PRED("HYPERTENSION") < 0.3',
        'DUMMY_RISK_PRED("HYPERTENSION") > 0.3',
        'AGE > 18 AND SEX = "FEMALE" AND (RAG_STATUS("Blood Pressure") = RED OR REP_COND("RS5PC-zIr8") OR DUMMY_HEALTHIQ() > 0.3 OR DUMMY_RISK_PRED("HYPERTENSION") > 0.3)',
        'AGE > 18',
        'REP_COND("RS5PC-zIr8") = TRUE',
        'REP_COND("RS5PC-zIr8") = FALSE',
        'RAG_STATUS("Blood Pressure") = RED OR RAG_STATUS("Blood Pressure") = AMBER',
        'REP_COND("UnknownID") = FALSE',
        'RAG_STATUS("UnknownID") = FALSE',
        'AT_LEAST(2, REP_COND("RS5PC-zIr8"), REP_COND("kxvgoB1X1b"), REP_COND("ktIvFMGdna"), REP_COND("YoTs_GRdm8"))',
        'AT_LEAST(1, REP_COND("RS5PC-zIr8"), REP_COND("kxvgoB1X1b"), REP_COND("ktIvFMGdna"), REP_COND("YoTs_GRdm8"))',
        'AT_LEAST(1, REP_COND("RS5PC-zIr8"), REP_COND("kxvgoB1X1b"), REP_COND("ktIvFMGdna"), REP_COND("YoTs_GRdm8")) AND (RAG_STATUS("Blood Pressure") = RED OR RAG_STATUS("Blood Pressure") = AMBER)',
    ]
# requests.post('https://services-uk.dev.babylontech.co.uk/babylon-advisor-eval/v1/evaluate_for_matching', json={
#   'patient_id': SOME_PATIENT_ID,
#   'extra_env_vars': {"N": 5},
#   'expressions': [
#       'AT_LEAST(' + str(some_var) + ', REP_COND("RS5PC-zIr8"), REP_COND("kxvgoB1X1b"), REP_COND("ktIvFMGdna"), REP_COND("YoTs_GRdm8"))',
#       'RAG_STATUS("Blood Pressure") = RED',
#       'RAG_STATUS("Blood Pressure") = AMBER',
#       'RAG_STATUS("Blood Pressure") = GREEN',
#       'RAG_STATUS("Blood Pressure") = GREY',
#   ]
# }).json()
def run_for_patient(patient_id):
    print("Patient ID:", patient_id)
    data = {
        'patient_id': patient_id,
        'expressions': expressions,
        'THIS_IS_EXPERIMENTAL_CODE': True,
    }
    result = requests.post('https://services-uk.dev.babylontech.co.uk/babylon-advisor-eval/v1/evaluate_for_matching', json=data).json()
    pprint(result)
    print("")
    for index, expression in enumerate(expressions):
        print(expression)
        pprint(result[index])
        print("")
    print("")
    print("")
    print("")
#run_for_patient("89e52f04-7f5d-4449-ac97-8f0217921b98")
run_for_patient("34a3ec35-707d-4167-9485-3c143cbea6f1")
# run_for_patient("76f4e28b-a87d-4a51-b4c4-67e623ace485")
# run_for_patient("e00e5266-15de-4c5f-a559-a1e3c8d683e4")