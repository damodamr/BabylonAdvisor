import json

with open('hypertension.json') as f:
  data = json.load(f)
  
#for item in data['concepts']:
    #print(item)

print("--------------")
def parseCoreography(guideline, cor):
    summaryBox = []
    for item in cor:
        if str(item).__contains__('/'):
            items = str(item).split('/')
            choose = getInfoAction(items)
            decision = input("Choose between actions " + str(choose))
            box = startAction(decision)
        else:
            box = startAction(item)
        summaryBox.append(box)

    print(guideline, summaryBox)

def getInfoAction(items):
    actionLabel = 'none'
    actionLabels = []
    for label in items:
        for item in data['concepts']:
            if 'actionID' in item:
                if item['actionID'] == label:
                    actionLabel = item['action']
                    actionLabels.append(label)
                    actionLabels.append(actionLabel)
                    if 'hasRequirement' in item:
                        reqs = item['hasRequirement']
                        required = collectRequirements(reqs)
                        actionLabels.append(required)
    return actionLabels


def startAction(label):
    required = []
    actionLabel = ""
    print('--------')
    print('Starting: ' + label)

    for item in data['concepts']:
        if 'actionID' in item:
            if item['actionID'] == label:
                actionLabel = item['action']
                print(actionLabel)
                if 'hasSnippet' in item:
                    info = item['hasSnippet']
                    print(info)
                if 'hasRequirement' in item:
                    reqs = item['hasRequirement']
                    required = collectRequirements(reqs)
    #print(required)

    satisfied = []
    for el in required:
        value = input("Is " + el + " satisfied (yes/no)? ")
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
                print(item['actionsCoreography'])
                parseCoreography(guideline, item['actionsCoreography'])


startGuideline("patient", 'Blood pressure measurement' )
