import streamlit as st
from tinydb import TinyDB, Query
import names
import random
import time

db = TinyDB('advisorPatientsInHG.json')

sbpNormal = random.randint(90, 119)
sbpElevated = random.randint(120, 129)
sbpStage1 = random.randint(130, 139)
sbpStage2 = random.randint(140, 179)
sbpCrisis = random.randint(180, 200)

dbpNormal = random.randint(60, 79)
dbpElevated = random.randint(0, 79)
dbpStage1 = random.randint(80, 89)
dbpStage2 = random.randint(90, 119)
dbpCrisis = random.randint(120, 140)

sbpdbpNormal = [sbpNormal, dbpNormal]
sbpdbpElevated = [sbpElevated, dbpElevated]
sbpdbpElevated2 = [sbpElevated, dbpNormal]
sbpdbpStage1 = [sbpStage1, dbpStage1]
sbpdbpStage1a = [sbpStage1, dbpElevated]
sbpdbpStage1b = [sbpStage1, dbpNormal]
sbpdbpStage1c = [sbpElevated, dbpStage1]
sbpdbpStage1d = [sbpNormal, dbpStage1]
sbpdbpStage2 = [sbpStage2, dbpStage2]
sbpdbpStage2a = [sbpStage2, dbpElevated]
sbpdbpStage2b = [sbpStage2, dbpNormal]
sbpdbpStage2c = [sbpElevated, dbpStage2]
sbpdbpStage2d = [sbpNormal, dbpStage2]
sbpdbpStage2e = [sbpStage2, dbpStage1]
sbpdbpStage2f = [sbpStage1, dbpStage2]
sbpdbpCrisis = [sbpCrisis, dbpCrisis]
sbpdbpCrisis1 = [sbpCrisis, dbpStage2]
sbpdbpCrisis2 = [sbpStage2, dbpCrisis]

elevatedBP = [sbpdbpElevated, sbpdbpElevated2]
stage1BP = [sbpdbpStage1, sbpdbpStage1a, sbpdbpStage1b, sbpdbpStage1c, sbpdbpStage1d]
stage2BP = [sbpdbpStage2, sbpdbpStage2a, sbpdbpStage2b, sbpdbpStage2c, sbpdbpStage2d, sbpdbpStage2e, sbpdbpStage2f]
crisisBP = [sbpdbpCrisis, sbpdbpCrisis1, sbpdbpCrisis2]
sbpdbp = [sbpdbpNormal, sbpdbpElevated, sbpdbpElevated2, sbpdbpStage1, sbpdbpStage1a, sbpdbpStage1b, sbpdbpStage1c, sbpdbpStage1d,
          sbpdbpStage2, sbpdbpStage2a, sbpdbpStage2b, sbpdbpStage2c, sbpdbpStage2d, sbpdbpStage2e, sbpdbpStage2f,
          sbpdbpCrisis, sbpdbpCrisis1, sbpdbpCrisis2]
randomSbpDbp = random.choice(sbpdbp)

tags = ["hypertension", "low back pain", "anxiety"]

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

under18 = random_dateUndeer18()
adult = random_dateAdult()
oldAge = random_dateOldAge()

dob = [under18, adult, oldAge]
randomDob = random.choice(dob)

gender = ["male", "female"]
randomGender = random.choice(gender)

pregnant = "DuLdf_kaOG"; ACEinhibitor = "R1JSUN6GdZ"; AngiotensinIIReceptorAntagonist = "GCtYSKFyHN"; ReninInhibitor = "FNqX5CkHk"
CCB = "3q8Z5tb8e8"; CKD = "ktIvFMGdna"; Albuminuria = "PDc0HGgCeL"; Thiazide = "H3e4IoNDWi"; Diabetes = "YoTs_GRdm8"; TransplantedKidney = "HhkA8Yw9GH"
HFpEF = "xkbKx4gqZ9"; PAD = "_uvf-5g2Qm"; CerebrovascularDisease = "ay9FqhhjBP"; StableAngina = "M4vJc4NwsO"; StableIHD = "qcfZrvyxPO"
AF = "m8m9GCRTo1"; AorticAneurysm = "iD3yFxsdrP"; HeartValveDisorder = "Ror64-IDlH"; none = "none"

conditionHypertension = [pregnant, CKD, Albuminuria, Diabetes, TransplantedKidney, HFpEF, PAD, CerebrovascularDisease,
                         StableAngina, StableIHD, AF, AorticAneurysm, HeartValveDisorder]
therapyHypertension = [ACEinhibitor, AngiotensinIIReceptorAntagonist, ReninInhibitor, CCB, Thiazide]
conditions = [none]

def getNames(gender):
    firstname = names.get_first_name(gender=gender)
    lastname = names.get_last_name()
    st.markdown("--------NAMING---------")
    if gender == 'male':
        firstName = st.text_input(
            'First name',
            value=firstname
        )
        surname = st.text_input(
            'Last name',
            value=lastname
        )
    if gender == 'female':
        firstName = st.text_input(
            'First name',
            value=firstname
        )
        surname = st.text_input(
            'Last name',
            value=lastname
        )

    return firstName, surname

def addPatient(firstName, surname, dob, gender):
    patient = {
            "name": firstName,
            "surname": surname,
            "dob": dob,
            "sex": gender,
            #"conditions": conditions,
            #"BP": randomSbpDbp,
            #"uuid": "",
            #"tag": tag
    }
    return patient

def main():
    st.sidebar.title('Create patient profile')
    st.sidebar.markdown("""Use the dropdown to select the guideline""")
    st.markdown("")


    st.markdown("")
    st.session_state.genders = [
        'male', 'female'
    ]
    st.session_state.gender = st.sidebar.radio(
        'Select the gender:',
        st.session_state.genders, on_change=getNames(st.session_state.gender)
    )

    st.sidebar.markdown("---")
    st.session_state.ages = [
        'adult', 'under 18', 'over 64'
    ]
    st.session_state.dob = st.sidebar.radio(
        'Select the age range:',
        st.session_state.ages
    )


    st.sidebar.markdown("---")
    st.session_state.pressures = [
        'Normal', 'Elevated', 'Stage 1', 'Stage 2', 'Stage Crisis'
    ]
    st.session_state.bpRanges = st.sidebar.radio(
        'Select the BP range:',
        st.session_state.pressures
    )


    # if st.session_state.gender == 'male':
    #     firstName = st.text_input(
    #         'First name',
    #         value=names.get_first_name(gender="male")
    #     )
    #     surname = st.text_input(
    #         'Last name',
    #         value=names.get_last_name()
    #     )
    # if st.session_state.gender == 'female':
    #     firstName = st.text_input(
    #         'First name',
    #         value=names.get_first_name(gender="female")
    #     )
    #     surname = st.text_input(
    #         'Last name',
    #         value=names.get_last_name()
    #     )

    st.markdown("--------DOB---------")

    if st.session_state.dob == 'adult':
        dob = st.text_input(
            'Date of birth',
            value= adult
        )
    if st.session_state.dob == 'under 18':
        dob = st.text_input(
            'Date of birth',
            value= under18
        )
    if st.session_state.dob == 'over 64':
        dob = st.text_input(
            'Date of birth',
            value= oldAge
        )

    st.markdown("--------BLOOD PRESSURE---------")

    if st.session_state.bpRanges == 'Normal':
        bpNormal = st.text_input(
            'Normal BP',
            value= sbpdbpNormal
        )
    if st.session_state.bpRanges == 'Elevated':
        bpElevated = st.text_input(
            'Elevated BP',
            value=random.choice(elevatedBP)
        )
    if st.session_state.bpRanges == 'Stage 1':
        bpStage1 = st.text_input(
            'Stage 1 BP',
            value=random.choice(stage1BP)
        )
    if st.session_state.bpRanges == 'Stage 2':
        bpStage2 = st.text_input(
            'Stage 2 BP',
            value=random.choice(stage2BP)
        )
    if st.session_state.bpRanges == 'Stage Crisis':
        bpCrisis = st.text_input(
            'Crisis BP',
            value=random.choice(crisisBP)
        )

    #if st.sidebar.button('Write the patient'):
    #pat = addPatient(firstName, surname, dob, gender)
    #st.write(pat)

if __name__ == "__main__":
  main()