class GamePhase(str, Enum):
    PLANNING = "planning"
    EXECUTION = "execution"
    RESET = "reset"

class UnitType(str, Enum):
    INFANTRY = "infantry"
    OFFICER = "officer"
    CAPTAIN = "captain"

class UnitStatus(str, Enum):
    ACTIVE = "active"
    ROUTED = "routed"
    RETREAT = "retreat"
    ELIMINATED = "eliminated"

class TerrainType(str, Enum):
    GRASS = "grass"
    WATER = "water"

class OrderType(str, Enum):
    ATTACK = "attack"
    MOVE = "move"
    DEPLOY = "deploy"
    DEFEND = "defend"
    CANCEL = "cancel"
