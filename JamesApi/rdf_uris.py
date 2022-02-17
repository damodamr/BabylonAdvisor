from rdflib import URIRef

# These are the list of hardcoded URIs that we use to power the prototype.
# For a more 'production' solution, these would not be hardcoded at the application layer,
# but instead loaded dynamically once WebProtege is properly integrated.


GUIDELINES_URI = {
    "guideline": URIRef("http://webprotege.stanford.edu/RidmHTIh9sOhg5Caq43scK")
}

PROCESS_URIS = {
    "process": URIRef("http://webprotege.stanford.edu/RBdZ9PjAPQbwHzyQfZFeimJ"),
    "blood_pressure_management": URIRef(
        "http://webprotege.stanford.edu/R7WEa3ShvTpTuqsAhGYqvHT"
    ),
}

ACTION_URIS = {
    "action": URIRef("http://webprotege.stanford.edu/RDuXbIDxtVhZiI5TPwjwXL4"),
}

PROPERTY_URIS = {
    "has_requirement": URIRef("http://webprotege.stanford.edu/RBKuVxv3Ag9NVQygDL8qwwX"),
    "has_age_requirement": URIRef(
        "http://webprotege.stanford.edu/RDuXbIDxtVhZiI5TPwjwXL4"
    ),
    "next": URIRef("http://webprotege.stanford.edu/RBX9yM6PnHMZmCut0ANkwK2"),
    "first": URIRef("http://webprotege.stanford.edu/RCYcJMTsWRUnM4fNdRyRf4S"),
    "has_snippet": URIRef("http://webprotege.stanford.edu/R9DtWPVELKDzTWPxZMDPCZb"),
    "snomed": URIRef("http://webprotege.stanford.edu/RCxRbA67sAZNNYGFNDdGHUe"),
    "babylon_code": URIRef("http://webprotege.stanford.edu/RBF8Invk9dtsgp4wQD68WeA"),
}
