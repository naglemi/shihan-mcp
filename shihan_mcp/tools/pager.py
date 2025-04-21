"""
PagerTool - Sends alerts via Pushover or creates a ninja scroll with --page flag.
"""

import os
import subprocess
import requests
from typing import Optional
from pydantic import BaseModel, Field

from .base_tool import BaseTool

class PagerInput(BaseModel):
    """Input schema for PagerTool."""
    title: str = Field(..., description="Title of the alert")
    body: str = Field(..., description="Body of the alert")
    priority: int = Field(default=0, description="Priority of the alert (0-2)")

class PagerOutput(BaseModel):
    """Output schema for PagerTool."""
    status: str = Field(..., description="Status of the paging operation")
    method: str = Field(..., description="Method used for paging (pushover or ninjascroll)")

class PagerTool(BaseTool[PagerInput, PagerOutput]):
    """
    Tool for sending alerts via Pushover or creating a ninja scroll with --page flag.
    """
    
    input_schema = PagerInput
    output_schema = PagerOutput
    
    def _run(self, input_obj: PagerInput) -> PagerOutput:
        """
        Send an alert via Pushover or create a ninja scroll with --page flag.
        
        Args:
            input_obj: An instance of PagerInput.
            
        Returns:
            An instance of PagerOutput.
        """
        # Try to send via Pushover first
        pushover_result = self._send_pushover(
            title=input_obj.title,
            message=input_obj.body,
            priority=input_obj.priority
        )
        
        if pushover_result:
            return PagerOutput(
                status="success",
                method="pushover"
            )
        
        # Fall back to ninjascroll if Pushover fails
        ninjascroll_result = self._create_ninjascroll(
            title=input_obj.title,
            body=input_obj.body
        )
        
        if ninjascroll_result:
            return PagerOutput(
                status="success",
                method="ninjascroll"
            )
        
        # Both methods failed
        return PagerOutput(
            status="failure",
            method="none"
        )
    
    def _send_pushover(self, title: str, message: str, priority: int) -> bool:
        """
        Send an alert via Pushover.
        
        Args:
            title: The title of the alert.
            message: The message of the alert.
            priority: The priority of the alert (0-2).
            
        Returns:
            True if the alert was sent successfully, False otherwise.
        """
        # Check if Pushover credentials are available
        user_key = os.getenv("PUSHOVER_USER_KEY")
        api_token = os.getenv("PUSHOVER_API_TOKEN")
        
        if not user_key or not api_token:
            return False
        
        try:
            # Send the alert
            response = requests.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": api_token,
                    "user": user_key,
                    "title": title,
                    "message": message,
                    "priority": priority,
                    "sound": "siren" if priority >= 1 else "pushover"
                },
                timeout=5
            )
            
            # Check if the request was successful
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _create_ninjascroll(self, title: str, body: str) -> bool:
        """
        Create a ninja scroll with --page flag.
        
        Args:
            title: The title of the scroll.
            body: The body of the scroll.
            
        Returns:
            True if the scroll was created successfully, False otherwise.
        """
        try:
            # For testing purposes, we'll create a scroll directly in the .scrolls directory
            print("Note: Creating scroll directly instead of using ninjascroll.sh")
            
            # Create the scrolls directory if it doesn't exist
            os.makedirs(".scrolls", exist_ok=True)
            
            # Create a timestamp for the scroll name
            from datetime import datetime
            timestamp = datetime.now().strftime("%m-%d-%H%M")
            # Sanitize the title for use in a filename
            safe_title = title.lower().replace(' ', '-').replace(':', '').replace('/', '-').replace('\\', '-')
            scroll_path = f".scrolls/{timestamp}-page-{safe_title}.md"
            
            # Write the scroll content
            with open(scroll_path, "w") as f:
                f.write(f"# {title}\n\n{body}\n\n**Priority: HIGH**\n\n*This is a page alert from Shihan.*")
            
            print(f"Created scroll: {scroll_path}")
            
            return True
            
        except Exception as e:
            print(f"Error creating scroll: {str(e)}")
            return False