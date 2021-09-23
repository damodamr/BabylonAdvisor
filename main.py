{
  "@id": "12345.1",
  "name": "Blood pressure measurement",
  "@context": "https://pathways.nice.org.uk/pathways/hypertension#path=view%3A/pathways/hypertension/hypertension-overview.xml&content=view-node%3Anodes-measuring-blood-pressure",
  "actionsCoreography": ["BP1", "BP2|BP3", "BP4", "BP5", "BP6"],
  "actions": [
      {"action": "check pulse",
       "actionID": "BP1",
       "hasOutcome": ["regular pulse","irregular pulse"]
       },
      {"action":"use automated device or manual checkup",
       "actionID": "BP2",
       "hasSnippet":"When measuring blood pressure in the clinic or in the home, standardise the environment and provide a relaxed, temperate setting, with the person quiet and seated, and their arm outstretched and supported. Use an appropriate cuff size for the person's arm.",
       "hasRequirement":"regular pulse"
       },
      {"action": "use manual checkup",
       "actionID": "BP3",
       "hasSnippet": "When measuring blood pressure in the clinic or in the home, standardise the environment and provide a relaxed, temperate setting, with the person quiet and seated, and their arm outstretched and supported. Use an appropriate cuff size for the person's arm.",
       "hasRequirement": "irregular pulse"
       },
      {"action": "checkup while lying down",
       "actionID": "BP4",
       "hasRequirement": ["postural dizziness/snomed:103017008", "history of falls/snomed:129839007", "type 2 diabetes/snomed:44054006"]
       },
      {"action": "checkup while standing",
       "actionID": "BP5",
       "hasRequirement": ["postural dizziness/snomed:103017008", "history of falls/snomed:129839007", "type 2 diabetes/snomed:44054006", "standing for 1 minute"]
       },
      {"action": ["review medication","measure subsequent blood pressures with the person standing", "consider referral to specialist care if symptoms of postural hypotension persist"],
       "actionID": "BP6",
       "hasRequirement": ["systolic blood pressure > 20 mmHg", "person is standing"]
       }
  ]
},
{
  "@id": "12345.2",
  "name": "Blood pressure diagnosis",
  "@context": "https://pathways.nice.org.uk/pathways/hypertension#path=view%3A/pathways/hypertension/hypertension-overview.xml&content=view-node%3Anodes-diagnosis",
  "actionsCoreography": [],
  "actions": [
      {"action": "offer ABMP",
       "actionID": "BPD1",
       "hasRequirement": ["clinic blood pressure between 140/90 mmHg and 180/110 mmHg", "at least 2 measurements per hour", "use average value of at least 14 measurements"]
       },
      {"action": "offer HBPM",
       "actionID": "BPD2",
       "hasRequirement": ["clinic blood pressure between 140/90 mmHg and 180/110 mmHg",
                          "tolerance/unsuitability to ABMP", "2 consecutive measurements are taken, at least 1 minute apart and with the person seated",
                          "blood pressure is recorded twice daily, ideally in the morning and evening", "blood pressure recording continues for at least 4 days, ideally for 7 days"]
       },
      {"action": "target organ damage",
       "actionID": "BPD3"
       },
      {"action": "formal assessment of cardiovascular risk",
       "actionID": "BPD4"
       },
      {"action": "confirm hypertension diagnosis",
       "actionID": "BPD5",
       "hasRequirement": ["clinic blood pressure >= 140/90 mmHg", "ABPM daytime average or HBPM average >= 135/85 mmHg"]
       }
    ]
}
