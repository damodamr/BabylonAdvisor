import requests
import json

def annotate(candidate):

    #r = requests.post('http://calculon.babylontech.co.uk:7798/ali-parser/v2/detect_entities',
                          #data=json.dumps({'Text': candidate}), headers={'Content-Type': 'application/json'})

    r = requests.post('https://services-uk.dev.babylontech.co.uk/nlp-understand-aliparser/parse',
                      data=json.dumps({'text': candidate}), headers={'Content-Type': 'application/json'})
    output = r.json()

    return output

text = "Mary complains of feeling ‘stressed’ all the time and constantly worries about" \
       "‘anything and everything’. She describes herself as always having been a" \
       "‘worrier’ but her anxiety has become much worse in the past 12 months since" \
       "her mother became unwell, and she no longer feels that she can control these" \
       "thoughts. When worried, Mary feels tension in her shoulders, stomach and" \
       "legs, her heart races and sometimes she finds it difficult to breathe. Her sleep" \
       "is poor with difficulty getting off to sleep due to worrying and frequent" \
       "wakening. She feels tired and irritable. She does not drink any alcohol."
dump = annotate(text)

print(dump)
for el in dump['entities']:
    if el['type'][0] == 'Clinical finding':
        print(el['text'])
        print(el['type'])
        print(el['coding'])
