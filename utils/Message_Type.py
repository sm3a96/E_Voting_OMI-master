from enum import Enum

class MESSAGE(Enum):
    DISCONNECT = 1
    CALCULATE_BALLOT = 2
    GENERATE_SHARES = 3
    COLLECTOR_REGISTRATION = 4
    COLLECT_STATUS = 5
    OTHER_COLLECTOR_INFO = 6
    VOTER_SIGNIN = 7
    VOTER_REGISTRATION = 8
    METADATA_VOTER = 9
    VOTERS_INFO = 10
    VOTER_LOCATION_AND_SHARES = 11
    VOTER_HEARTBEAT = 12
    LAS1 = 13
    LAS2= 14
    VOTER_BALLOTS = 15
