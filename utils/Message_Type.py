from enum import Enum

class MESSAGE(Enum):
    DISCONNECT = 1
    CALCULATE_BALLOT = 2
    GENERATE_SHARES = 3
    COLLECT_REQUEST = 4
    COLLECT_STATUS = 5
    METADATA_COLL = 6
    VOTER_SIGNIN = 7
    VOTER_REGISTRATION = 8
    METADATA_VOTER = 9
    VOTERS_INFO = 10