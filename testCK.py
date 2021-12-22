import requests

def ck2(iri, code):
    while True:
        try:
            results = requests.get('https://services.global1.dev.babylontech.co.uk/clinical-knowledge/v2/ids/code?iri='+iri+'&system='+code).json()
        except Exception:
            print("ck problem")
            continue
        break
    return results

print(ck2("https://bbl.health/YoTs_GRdm8", "SNOMEDCT"))