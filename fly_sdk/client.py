import requests
from typing import Optional, List, Dict, Any
from fly_sdk.models.machine import Machine, MachineConfig
from fly_sdk.models.errors import FlyAPIError

class FlyClient:
    """
    Main client for interacting with the Fly.io API.
    """
    
    def __init__(
        self, 
        api_token: str, 
        base_url: str = "https://api.fly.io/v1"
    ):
        """
        Initialize the Fly API client.

        Args:
            api_token (str): Your Fly.io API token
            base_url (str, optional): Base URL for the Fly API. Defaults to "https://api.fly.io/v1"
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        })

    def list_machines(self, app_name: str) -> List[Machine]:
        """
        List all machines for a given app.

        Args:
            app_name (str): Name of the Fly app

        Returns:
            List[Machine]: List of machines

        Raises:
            FlyAPIError: If the API request fails
        """
        response = self.session.get(f"{self.base_url}/apps/{app_name}/machines")
        
        if response.status_code != 200:
            raise FlyAPIError(
                f"Failed to list machines: {response.status_code}",
                response
            )
            
        return [Machine.parse_obj(machine) for machine in response.json()]

    def get_machine(self, app_name: str, machine_id: str) -> Machine:
        """
        Get details for a specific machine.

        Args:
            app_name (str): Name of the Fly app
            machine_id (str): ID of the machine

        Returns:
            Machine: Machine details

        Raises:
            FlyAPIError: If the API request fails
        """
        response = self.session.get(
            f"{self.base_url}/apps/{app_name}/machines/{machine_id}"
        )
        
        if response.status_code != 200:
            raise FlyAPIError(
                f"Failed to get machine: {response.status_code}",
                response
            )
            
        return Machine.parse_obj(response.json())

    def create_machine(
        self, 
        app_name: str, 
        config: MachineConfig
    ) -> Machine:
        """
        Create a new machine.

        Args:
            app_name (str): Name of the Fly app
            config (MachineConfig): Machine configuration

        Returns:
            Machine: Created machine details

        Raises:
            FlyAPIError: If the API request fails
        """
        response = self.session.post(
            f"{self.base_url}/apps/{app_name}/machines",
            json=config.dict(exclude_none=True)
        )
        
        if response.status_code != 201:
            raise FlyAPIError(
                f"Failed to create machine: {response.status_code}",
                response
            )
            
        return Machine.parse_obj(response.json())
