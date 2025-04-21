"""
WatchdogAgent - Orchestrates tools to enforce the Creed and supervise Hayato's work.
"""

import os
import glob
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from ..tools.log_tail import LogSentinelTool
from ..tools.creed_audit import CreedAuditTool
from ..tools.plan_critic import PlanCriticTool
from ..tools.pager import PagerTool
from ..config import Paths

class WatchInput(BaseModel):
    """Input schema for WatchdogAgent."""
    event: Literal["cycle_end", "manual_check", "scroll_committed"] = Field(
        ..., description="Event that triggered the watchdog"
    )
    scroll_path: Optional[str] = Field(
        None, description="Path to the ninja scroll that was committed"
    )

class WatchOutput(BaseModel):
    """Output schema for WatchdogAgent."""
    status: str = Field(..., description="Status of the watchdog operation")
    actions_taken: List[str] = Field(default_factory=list, description="List of actions taken by the watchdog")
    issues_found: List[str] = Field(default_factory=list, description="List of issues found by the watchdog")
    paged: bool = Field(default=False, description="Whether a page was sent")

class WatchdogAgent:
    """
    Agent that orchestrates tools to enforce the Creed and supervise Hayato's work.
    """
    
    def __init__(self):
        """Initialize the watchdog agent with its tools."""
        self.log_sentinel = LogSentinelTool()
        self.creed_audit = CreedAuditTool()
        self.plan_critic = PlanCriticTool()
        self.pager = PagerTool()
    
    def run(self, input_obj: WatchInput) -> WatchOutput:
        """
        Run the watchdog agent based on the input event.
        
        Args:
            input_obj: An instance of WatchInput.
            
        Returns:
            An instance of WatchOutput.
        """
        actions_taken = []
        issues_found = []
        paged = False
        
        if input_obj.event == "cycle_end":
            # Handle cycle end event
            result = self._handle_cycle_end()
            actions_taken.extend(result["actions_taken"])
            issues_found.extend(result["issues_found"])
            paged = result["paged"]
            
        elif input_obj.event == "scroll_committed" and input_obj.scroll_path:
            # Handle scroll committed event
            result = self._handle_scroll_committed(input_obj.scroll_path)
            actions_taken.extend(result["actions_taken"])
            issues_found.extend(result["issues_found"])
            paged = result["paged"]
            
        elif input_obj.event == "manual_check":
            # Handle manual check event
            result = self._handle_manual_check()
            actions_taken.extend(result["actions_taken"])
            issues_found.extend(result["issues_found"])
            paged = result["paged"]
        
        return WatchOutput(
            status="completed",
            actions_taken=actions_taken,
            issues_found=issues_found,
            paged=paged
        )
    
    def _handle_cycle_end(self) -> dict:
        """
        Handle the cycle_end event.
        
        Returns:
            A dictionary with the results of the operation.
        """
        actions_taken = []
        issues_found = []
        paged = False
        
        # Step 1: Check the log for errors
        actions_taken.append("Checking log for errors")
        log_result = self.log_sentinel.run({"tail_lines": 500})
        
        if log_result.get("last_error"):
            # Error found in log
            issues_found.append(f"Error found in log: {log_result.get('last_error')}")
            
            # Page Hayato
            actions_taken.append("Paging Hayato about log error")
            page_result = self.pager.run({
                "title": "Error detected in training log",
                "body": f"Shihan has detected an error in the training log:\n\n{log_result.get('last_error')}",
                "priority": 1
            })
            
            if page_result.get("status") == "success":
                actions_taken.append(f"Paged successfully via {page_result.get('method')}")
                paged = True
            else:
                issues_found.append("Failed to page Hayato")
        
        else:
            # No error in log, check for changed files
            actions_taken.append("No errors found in log, checking for changed files")
            
            # Get list of changed files (using git status)
            changed_files = self._get_changed_files()
            
            if changed_files:
                # Audit changed files
                actions_taken.append(f"Auditing {len(changed_files)} changed files")
                audit_result = self.creed_audit.run({"files": changed_files})
                
                if audit_result.get("violations"):
                    # Violations found
                    issues_found.extend(audit_result.get("violations"))
                    
                    # Page Hayato
                    actions_taken.append("Paging Hayato about creed violations")
                    page_result = self.pager.run({
                        "title": "Creed violations detected",
                        "body": f"Shihan has detected {len(audit_result.get('violations'))} creed violations:\n\n" + 
                                "\n".join(audit_result.get("violations")),
                        "priority": 1
                    })
                    
                    if page_result.get("status") == "success":
                        actions_taken.append(f"Paged successfully via {page_result.get('method')}")
                        paged = True
                    else:
                        issues_found.append("Failed to page Hayato")
                else:
                    actions_taken.append("No creed violations found")
            else:
                actions_taken.append("No changed files found")
        
        return {
            "actions_taken": actions_taken,
            "issues_found": issues_found,
            "paged": paged
        }
    
    def _handle_scroll_committed(self, scroll_path: str) -> dict:
        """
        Handle the scroll_committed event.
        
        Args:
            scroll_path: Path to the ninja scroll that was committed.
            
        Returns:
            A dictionary with the results of the operation.
        """
        actions_taken = []
        issues_found = []
        paged = False
        
        # Critique the plan
        actions_taken.append(f"Critiquing plan: {scroll_path}")
        critique_result = self.plan_critic.run({"scroll_path": scroll_path})
        
        # Check if the score is below the threshold
        if critique_result.get("score", 0) < 80:
            # Score is below threshold
            issues_found.append(f"Plan score is below threshold: {critique_result.get('score')}/100")
            issues_found.extend(critique_result.get("issues", []))
            
            # Page Hayato
            actions_taken.append("Paging Hayato about low plan score")
            page_result = self.pager.run({
                "title": f"Plan critique: {critique_result.get('score')}/100",
                "body": f"Shihan has critiqued your plan and found issues:\n\n" + 
                        "\n".join(critique_result.get("issues", [])),
                "priority": 1
            })
            
            if page_result.get("status") == "success":
                actions_taken.append(f"Paged successfully via {page_result.get('method')}")
                paged = True
            else:
                issues_found.append("Failed to page Hayato")
        else:
            actions_taken.append(f"Plan score is acceptable: {critique_result.get('score')}/100")
        
        return {
            "actions_taken": actions_taken,
            "issues_found": issues_found,
            "paged": paged
        }
    
    def _handle_manual_check(self) -> dict:
        """
        Handle the manual_check event.
        
        Returns:
            A dictionary with the results of the operation.
        """
        actions_taken = []
        issues_found = []
        paged = False
        
        # Check the log
        log_result = self._handle_cycle_end()
        actions_taken.extend(log_result["actions_taken"])
        issues_found.extend(log_result["issues_found"])
        paged = log_result["paged"]
        
        # Check the latest scroll if available
        latest_scroll = self._get_latest_scroll()
        if latest_scroll:
            actions_taken.append(f"Found latest scroll: {latest_scroll}")
            scroll_result = self._handle_scroll_committed(latest_scroll)
            actions_taken.extend(scroll_result["actions_taken"])
            issues_found.extend(scroll_result["issues_found"])
            paged = paged or scroll_result["paged"]
        else:
            actions_taken.append("No recent scrolls found")
        
        return {
            "actions_taken": actions_taken,
            "issues_found": issues_found,
            "paged": paged
        }
    
    def _get_changed_files(self) -> List[str]:
        """
        Get a list of changed files using git status.
        
        Returns:
            A list of changed file paths.
        """
        try:
            import subprocess
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Filter for Python files
                return [
                    file for file in result.stdout.strip().split("\n")
                    if file and file.endswith((".py", ".pyx", ".pyi"))
                ]
            
            return []
            
        except Exception:
            return []
    
    def _get_latest_scroll(self) -> Optional[str]:
        """
        Get the path to the latest ninja scroll.
        
        Returns:
            The path to the latest scroll, or None if no scrolls are found.
        """
        try:
            # Get all markdown files in the scrolls directory
            scrolls_dir = Paths.SCROLLS
            if not os.path.exists(scrolls_dir):
                return None
            
            scrolls = glob.glob(os.path.join(scrolls_dir, "*.md"))
            
            if not scrolls:
                return None
            
            # Sort by modification time (newest first)
            scrolls.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return scrolls[0]
            
        except Exception:
            return None