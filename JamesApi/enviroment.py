import pathlib
import os

#RDF_PATH = os.environ.get(
#    "ADVISOR_RDF_PATH", str(pathlib.Path().resolve() / "core" / "prototype_data.owl")
#)

RDF_PATH = "/Users/damir.juric/PycharmProjects/babylon-advisor/urn_webprotege_ontology_8c5fd0ff-d7ef-4e72-8e06-462eebaba042.owl"

HEALTHGRAPH_URL = os.environ.get(
    "ADVISOR_HEALTHGRAPH_URL", "https://services-uk.dev.babylontech.co.uk/chr/graphql"
)
AUTH_URL = os.environ.get(
    #"ADVISOR_AUTH_URL", "https://services-uk.dev.babylontech.co.uk/ai-auth/v1/internal",
    "ADVISOR_AUTH_URL", "https://auth.global1.dev.babylontech.co.uk/oauth/token"
)

CLIENT_ID = "1M1m7EKIyUg6e3xdDWJQEFBt4a3F3uyE"
CLIENT_SECRET = "42drt7aEQTfWLnThhsJ5woWJmYkFJwN0bmKXz38rKjGmseW3d31aavY4q7ZLMiSN"