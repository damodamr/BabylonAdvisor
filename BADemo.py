import streamlit as st
import json

STYLE = """
<style>
img {
    max-width: 100%;
}
</style>
"""

# @st.cache(allow_output_mutation=True)
# def load_json():
#     with open('hypertension.json') as f:
#         data = json.load(f)
#     return data

with open('hypertension.json') as f:
    data = json.load(f)

def parseCoreography(guideline, cor):
    decision = "none"
    flag = 1
    box = []
    summaryBox = []

    for item in cor:
        if st.button(item):
            st.write('Starting ' + item)
            st.write(getInfoAction(item))




def getInfoAction(items):
    actionLabel = 'none'
    actionLabels2 = []
    for label in items:
        actionLabels = []
        for item in data['concepts']:
            if 'actionID' in item:
                if item['actionID'] == label:
                    print("here3")
                    actionLabel = item['action']
                    actionLabels.append(label)
                    actionLabels.append(actionLabel)
                    if 'hasRequirement' in item:
                        reqs = item['hasRequirement']
                        required = collectRequirements(reqs)
                        actionLabels.append(required)
        actionLabels2.append(actionLabels)
        print(actionLabels2)
    return actionLabels2


def startAction(label):
    required = []
    actionLabel = ""
    print('--------')
    st.write('Starting: ' + label)
    print('Starting: ' + label)

    for item in data['concepts']:
        if 'actionID' in item:
            if item['actionID'] == label:
                actionLabel = item['action']
                print(actionLabel)
                st.write(actionLabel)
                if 'hasSnippet' in item:
                    info = item['hasSnippet']
                    print(info)
                    st.write(info)
                if 'hasRequirement' in item:
                    reqs = item['hasRequirement']
                    required = collectRequirements(reqs)
    #print(required)

    satisfied = []
    for el in required:
        #value = input("Is " + el + " satisfied (yes/no)? ")
        default_value_goes_here = 'no'
        value = st.text_input("Is " + str(el) + " satisfied (yes/no)? ", default_value_goes_here)
        satisfied.append(value)
    #print(satisfied)
    print("Finished " + label)
    return(actionLabel, required, satisfied)

def collectRequirements(reqs):
    required = []
    for el in reqs:
        ell = str(el.replace('node:', ''))
        for item in data['concepts']:
            if 'conceptID' in item:
                for item2 in item['entities']:
                    if item2['conceptID'] == ell:
                        required.append(item2['label'])

    return required

def startGuideline(patientdata, guideline):

    for item in data['concepts']:
        #print(item)
        if 'label' in item:
            if item['label'] == guideline:
                cor = item['actionsCoreography']
                #parseCoreography(guideline, item['actionsCoreography'])
    return cor

def main():
    """Run this function to display the Streamlit app"""

    st.sidebar.title('Babylon Advisor')
    st.sidebar.markdown("""Use the dropdown to select the guideline and patient data""")
    st.markdown(STYLE, unsafe_allow_html=True)
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
    cor = startGuideline(patient_type, guideline_type)
    if st.sidebar.button('Show actions'):
        st.write(cor)

    if st.sidebar.button("Start"):
        print('here')
        st.write('Starting ' + str(cor[0]))

        st.write(startAction(cor[0]))
        st.write(startAction(cor[1]))

main()