from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class MachineState(str, Enum):
    DESTROYED = "destroyed"
    DESTROYING = "destroying"
    STARTED = "started"
    STOPPED = "stopped"
    SUSPENDED = "suspended"
    CREATED = "created"

class HostStatus(str, Enum):
    OK = "ok"
    UNKNOWN = "unknown"
    UNREACHABLE = "unreachable"

class Machine(BaseModel):
    id: str
    name: str
    state: MachineState
    region: str
    instance_id: Optional[str] = None
    private_ip: Optional[str] = None
    config: Optional['MachineConfig'] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        use_enum_values = True

class MachineConfig(BaseModel):
    image: str
    env: Optional[Dict[str, str]] = None
    services: Optional[List[Dict[str, Any]]] = None
    guest: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"
