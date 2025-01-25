from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Any
import time
import json
from datetime import datetime

# Constants
MACHINE_CONFIG_METADATA_KEY_FLY_MANAGED_POSTGRES = "fly-managed-postgres"
MACHINE_CONFIG_METADATA_KEY_FLY_PLATFORM_VERSION = "fly_platform_version"
MACHINE_CONFIG_METADATA_KEY_FLY_RELEASE_ID = "fly_release_id"
MACHINE_CONFIG_METADATA_KEY_FLY_RELEASE_VERSION = "fly_release_version"
MACHINE_CONFIG_METADATA_KEY_FLY_PROCESS_GROUP = "fly_process_group"
MACHINE_CONFIG_METADATA_KEY_FLY_PREVIOUS_ALLOC = "fly_previous_alloc"
MACHINE_CONFIG_METADATA_KEY_FLYCTL_VERSION = "fly_flyctl_version"
MACHINE_CONFIG_METADATA_KEY_FLYCTL_BG_TAG = "fly_bluegreen_deployment_tag"

MACHINE_FLY_PLATFORM_VERSION_2 = "v2"
MACHINE_PROCESS_GROUP_APP = "app"
MACHINE_PROCESS_GROUP_FLY_APP_RELEASE_COMMAND = "fly_app_release_command"
MACHINE_PROCESS_GROUP_FLY_APP_TEST_MACHINE_COMMAND = "fly_app_test_machine_command"
MACHINE_PROCESS_GROUP_FLY_APP_CONSOLE = "fly_app_console"

# Machine States
class MachineState(str, Enum):
    DESTROYED = "destroyed"
    DESTROYING = "destroying"
    STARTED = "started"
    STOPPED = "stopped"
    SUSPENDED = "suspended"
    CREATED = "created"

# Host Status
class HostStatus(str, Enum):
    OK = "ok"
    UNKNOWN = "unknown"
    UNREACHABLE = "unreachable"

@dataclass
class MachineImageRef:
    registry: str
    repository: str
    tag: str
    digest: str
    labels: Dict[str, str]

@dataclass
class Machine:
    id: str
    name: str
    state: str
    region: str
    image_ref: MachineImageRef
    instance_id: str
    version: str
    private_ip: str
    created_at: str
    updated_at: str
    config: Optional['MachineConfig']
    events: List['MachineEvent']
    checks: List['MachineCheckStatus']
    lease_nonce: str
    host_status: HostStatus
    incomplete_config: Optional['MachineConfig']

    def full_image_ref(self) -> str:
        img_str = f"{self.image_ref.registry}/{self.image_ref.repository}"
        tag = self.image_ref.tag
        digest = self.image_ref.digest

        if tag and digest:
            return f"{img_str}:{tag}@{digest}"
        elif digest:
            return f"{img_str}@{digest}"
        elif tag:
            return f"{img_str}:{tag}"
        return img_str

    def image_ref_with_version(self) -> str:
        ref = f"{self.image_ref.repository}:{self.image_ref.tag}"
        version = self.image_ref.labels.get("fly.version", "")
        if version:
            ref = f"{ref} ({version})"
        return ref

    def get_config(self) -> Optional['MachineConfig']:
        return self.config if self.config else self.incomplete_config

    def get_metadata_by_key(self, key: str) -> str:
        config = self.get_config()
        if not config or not config.metadata:
            return ""
        return config.metadata.get(key, "")

    def is_apps_v2(self) -> bool:
        return self.get_metadata_by_key(MACHINE_CONFIG_METADATA_KEY_FLY_PLATFORM_VERSION) == MACHINE_FLY_PLATFORM_VERSION_2

    def is_active(self) -> bool:
        return self.state not in [MachineState.DESTROYED, MachineState.DESTROYING]

@dataclass
class MachineEvent:
    type: str
    status: str
    request: Optional['MachineRequest']
    source: str
    timestamp: int

    def time(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp / 1000)

@dataclass
class MachineConfig:
    env: Dict[str, str]
    init: 'MachineInit'
    guest: Optional['MachineGuest']
    metadata: Dict[str, str]
    mounts: List['MachineMount']
    services: List['MachineService']
    metrics: Optional['MachineMetrics']
    checks: Dict[str, 'MachineCheck']
    image: str
    files: List['File']
    schedule: str
    auto_destroy: bool
    restart: Optional['MachineRestart']
    dns: Optional['DNSConfig']
    processes: List['MachineProcess']
    standbys: List[str]
    stop_config: Optional['StopConfig']
    containers: List['ContainerConfig']
    volumes: List['VolumeConfig']

    def process_group(self) -> str:
        if not self.metadata:
            return ""
        
        fly_process_group = self.metadata.get(MACHINE_CONFIG_METADATA_KEY_FLY_PROCESS_GROUP, "")
        if fly_process_group:
            return fly_process_group
        
        return self.metadata.get("process_group", "")
