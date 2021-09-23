import streamlit as st
import json

with open('hypertension.json') as f:
    data = json.load(f)

def patientInfo(required, patient_type):
    patient = []
    satisfied = []
    patientA = ['type 2 diabetes', 'history of falls']
    patientB = ['postural dizziness', 'history of falls', 'type 2 diabetes']
    patientC = ['postural dizziness']
    patientD = ['type 1 diabetes']

    if patient_type == 'Patient A':
        patient = patientA
    if patient_type == 'Patient B':
        patient = patientB
    if patient_type == 'Patient C':
        patient = patientC
    if patient_type == 'Patient D':
        patient = patientD

    for el in required:
        if el in patient:
            satisfied.append('yes')
        else:
            satisfied.append('no')
    return satisfied


def collectRequirements(reqs):
    required = []
    extra = []
    for el in reqs:
        extra2 = []
        ell = str(el.replace('node:', ''))
        for item in data['concepts']:
            if 'conceptID' in item:
                for item2 in item['entities']:
                    if item2['conceptID'] == ell:
                        required.append(item2['label'])
                        extra.append(item2['label'])
                        if item2['snomed']:
                            extra2.append(item2['snomed'])
                            extra2.append("https://snomedbrowser.com/Codes/Details/" + item2['snomed'])
                        if item2['isa']:
                            extra2.append(item2['isa'])
        extra.append(extra2)

    return required, extra

def startAction(label, patient_type):
    required = []
    extra = []
    actionSummary = []
    actionLabel = "label"
    info = "no info"
    print('Starting: ' + label)

    if str(label).__contains__('/') == False:
        for item in data['concepts']:
            if 'actionID' in item:
                if item['actionID'] == label:
                    actionLabel = item['action']
                    if 'hasSnippet' in item:
                        info = item['hasSnippet']
                    if 'hasRequirement' in item:
                        reqs = item['hasRequirement']
                        required, extra = collectRequirements(reqs)

                    st.subheader("Action name: " + actionLabel)
                    st.info("Additional information: " + info)
                    st.write(required)
                    with st.beta_expander("See metadata"):
                        st.write(extra)
                    satisfied = []
                    satisfied2 = []
                    counterB = 0
                    counterBB = 1000
                    counterBBB = 10000
                    if len(required) > 0:
                        st.success('Manually adjust the satisfied requirements')
                        for el in required:
                            agree = st.checkbox(el, key=str(counterB))
                            counterB = counterB + 1
                            if agree:
                                satisfied2.append('yes')
                            else:
                                satisfied2.append('no')

                        #st.write(satisfied2)
                        if st.button('Save selected requirements', key = 'BB'):
                            st.info('Saved')

                        st.success('Or load existing patient from Babylon services')
                        if st.button('Load patient data', key=str(counterBB)):
                            satisfied = patientInfo(required, patient_type)
                        st.write(satisfied)
                        if st.button('Save loaded patient data' , key = 'BBB'):
                            st.info('Saved')
                    actionSummary.append(actionLabel)
                    actionSummary.append(required)
                    satisfied = []
                    satisfied2 = []

    if str(label).__contains__('/'):
        labels = label.split('/')
        st.info("Decision must be made!")
        st.markdown("---")

        for item in data['concepts']:
            if 'actionID' in item:
                if item['actionID'] == labels[0]:
                    actionLabel = item['action']
                    if 'hasSnippet' in item:
                        info = item['hasSnippet']
                    if 'hasRequirement' in item:
                        reqs = item['hasRequirement']
                        required, extra = collectRequirements(reqs)

                    st.subheader("Action name: " + actionLabel)
                    st.info("Additional information: " + info)
                    st.write(required)
                    with st.beta_expander("See metadata"):
                        st.write(extra)

                    if len(required) > 0:
                        st.success('Manually adjust the satisfied requirements')
                    satisfied = []
                    satisfied2 = []
                    counter0 = 100
                    counterBB = 2000
                    counterBBB = 20000
                    for el in required:
                        agree0 = st.checkbox(el, key=str(counter0))
                        counter0 = counter0 + 1
                        if agree0:
                            satisfied2.append('yes')
                        else:
                            satisfied2.append('no')

                    #st.write(satisfied2)
                    if st.button('Save selected requirements', key = '00'):
                        st.info('Saved')
                    if len(required) > 0:
                        st.success('Or load existing patient from Babylon services')
                    if st.button('Load patient data', key=str(counterBB)):
                        satisfied = patientInfo(required, patient_type)

                    st.write(satisfied)
                    if st.button('Save loaded patient data', key = '000'):
                        st.info('Saved')
                    actionSummary.append(actionLabel)
                    actionSummary.append(required)
                    satisfied = []
                    satisfied2 = []

                    st.markdown("---")
                    st.markdown("---")

                if item['actionID'] == labels[1]:
                    actionLabel = item['action']
                    if 'hasSnippet' in item:
                        info = item['hasSnippet']
                    if 'hasRequirement' in item:
                        reqs = item['hasRequirement']
                        required, extra = collectRequirements(reqs)

                    st.subheader("Action name: " + actionLabel)
                    st.info("Additional information: " + info)
                    st.write(required)
                    with st.beta_expander("See metadata"):
                        st.write(extra)
                    if len(required) > 0:
                        st.success('Manually adjust the satisfied requirements')
                    satisfied = []
                    satisfied2 = []
                    counter1 = 200
                    counter11 = 3000
                    counter111 = 30000
                    for el1 in required:
                        agree1 = st.checkbox(el1 , key=str(counter1))
                        counter1 = counter1 + 1
                        if agree1:
                            satisfied2.append('yes')
                        else:
                            satisfied2.append('no')
                    #st.write(satisfied2)
                    if st.button('Save selected requirements', key = '11'):
                        st.info('Saved')
                    if len(required) > 0:
                        st.success('Or load existing patient from Babylon services')
                    if st.button('Load patient data', key=str(counter11)):
                        satisfied = patientInfo(required, patient_type)

                    st.write(satisfied)
                    if st.button('Save loaded patient data', key = '111'):
                        st.info('Saved')
                    actionSummary.append(actionLabel)
                    actionSummary.append(required)
                    satisfied = []
                    satisfied2 = []

                    st.markdown("---")

    return(actionSummary)

def showActions(patientdata, guideline):
    cor = []
    for item in data['concepts']:
        if 'label' in item:
            if item['label'] == guideline:
                cor = item['actionsCoreography']
    return cor

def main():
    """Run this function to display the Streamlit app"""
    summary = []
    st.sidebar.title('Babylon Advisor')
    st.sidebar.markdown("""Use the dropdown to select the guideline and patient data""")
    #st.markdown(STYLE, unsafe_allow_html=True)
    guideline_type = st.sidebar.selectbox(
        'Select the guideline',
        ('','Blood pressure measurement', 'more to come...'),
        index=0
    )

    patient_type = st.sidebar.selectbox(
        'Load the patient data',
        ('','Patient A', 'Patient B', 'Patient C', 'Patient D'),
        index=0
    )

    st.sidebar.markdown("---")

    cor = showActions(patient_type, guideline_type)
    if st.sidebar.button('Show actions'):
        st.write(cor)

    if 'count' not in st.session_state:
        st.session_state.count = 0

    increment = st.button('Suggest next Action')
    decrement = st.button('Go back')
    if increment:
        st.session_state.count += 1
    if decrement:
        st.session_state.count += -1

    number = st.session_state.count

    if number in range(0,len(cor)):
        st.header("Action: " + str(number + 1))
        st.header('Starting action id: ' + str(cor[int(number)]))
        sum = startAction(cor[int(number)], patient_type)
        summary.append(sum)

    #else:
        #st.write("Finished")
        #st.write(summary)

main()