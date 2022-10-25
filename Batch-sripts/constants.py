import urllib3

UPLOAD_TIMEOUT = urllib3.Timeout(connect=60, read=600)

THREEDI_API_HOST = "https://api.3di.live"
ORGANISATION_UUID = " --- "  # Fill in your organisation UUID
RADAR_ID = "d6c2347d-7bd1-4d9d-a1f6-b342c865516f"
deelgebieden_fn = "Path to your submodels"

SCHEMATISATIONS = [
   "Name of your schematisation",
]





BUIEN = {
    'XXmm': [  # s, m/s
        [0,         35 / (1000 * 60 * 60)],
        [60*60,         0]
    ]
    ,
    'XXmm': [  # s, m/s
        [0,         70 / (1000 * 60 * 60)],
        [60*60,         0]
    ]

    
}
