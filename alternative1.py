{
    "concepts":[
        {
          "@id": "12345.1",
          "label": "Blood pressure measurement",
          "@context": "https://pathways.nice.org.uk/pathways/hypertension#path=view%3A/pathways/hypertension/hypertension-overview.xml&content=view-node%3Anodes-measuring-blood-pressure",
          "actionsCoreography": ["node:chkpls", "node:uadomc|node:umc", "node:cwld", "node:cws", "node:rmacrts"]
        },
        {
            "action": "check pulse",
            "actionID": "chkpls",
            "hasOutcome": ["node:rp","node:irp"]
        },
        {
            "action":"use automated device or manual checkup",
            "actionID": "uadomc",
            "hasSnippet":"When measuring blood pressure in the clinic or in the home, standardise the environment and provide a relaxed, temperate setting, with the person quiet and seated, and their arm outstretched and supported. Use an appropriate cuff size for the person's arm.",
            "hasRequirement":"node:rp"
        },
        {
            "action": "use manual checkup",
            "actionID": "umc",
            "hasSnippet": "When measuring blood pressure in the clinic or in the home, standardise the environment and provide a relaxed, temperate setting, with the person quiet and seated, and their arm outstretched and supported. Use an appropriate cuff size for the person's arm.",
            "hasRequirement": "node:irp"
        },
        {
            "action": "checkup while lying down",
            "actionID": "cwld",
            "hasRequirement": ["node:pd", "node:hof", "node:t2d"]
        },
        {
            "action": "checkup while standing",
            "actionID": "cws",
            "hasRequirement": ["node:pd", "node:of", "node:t2d", "node:s1m"]
        },
        {
            "action": "review medication and consider referral to specialist",
            "hasSnippet": "review medication and consider referral to specialist care if symptoms of postural hypotension persist",
            "actionID": "rmacrts",
            "hasRequirement": ["node:sbp20", "node:pis"]
        },
        {
            "conceptID": "oe",
            "label": "observable entity",
            "entities":[
                {
                    "conceptID": "sbp20",
                    "label": "systolic blood pressure > 20 mmHg",
                    "snomed": "???",
                    "isa": "observable entity"
                },
                {
                    "conceptID": "pis",
                    "label": "person is standing",
                    "snomed": "???",
                    "isa": "observable entity"
                },
                {
                    "conceptID": "s1m",
                    "label": "standing for 1 minute",
                    "snomed": "???",
                    "isa": "observable entity"
                }
            ]
        },
        {
            "conceptID": "fin",
            "label": "finding",
            "entities":[
                {
                    "conceptID": "pd",
                    "label": "postural dizziness",
                    "snomed": "103017008",
                    "isa": "finding"
                },
                {
                    "conceptID": "hof",
                    "label": "history of falls",
                    "snomed": "129839007",
                    "isa": "finding"
                },
                {
                    "conceptID": "t2d",
                    "label": "type 2 diabetes",
                    "snomed": "44054006",
                    "isa": "finding"
                },
                {
                    "conceptID": "rp",
                    "label": "regular pulse",
                    "snomed": "271636001",
                    "isa": "finding"
                },
                {
                    "conceptID": "irp",
                    "label": "irregular pulse",
                    "snomed": "61086009",
                    "isa": "finding"
                }
            ]
        }
    ]
}