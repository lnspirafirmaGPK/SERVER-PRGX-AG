from enum import Enum


class EthicalStatus(str, Enum):
    CLEAN = "CLEAN"
    MINOR_INFRACTION = "MINOR_INFRACTION"
    MAJOR_VIOLATION = "MAJOR_VIOLATION"
    PARAJIKA = "PARAJIKA"


class IntentType(str, Enum):
    QUERY = "QUERY"
    COMMAND = "COMMAND"
    TRANSACTION = "TRANSACTION"
    SYSTEM_UPDATE = "SYSTEM_UPDATE"


class AuditStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
