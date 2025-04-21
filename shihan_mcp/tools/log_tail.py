"""
LogSentinelTool - Tails, parses, and summarizes training.log and crash traces.
"""

import re
import subprocess
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from ..config import Paths
from .base_tool import BaseTool

class LogSentinelInput(BaseModel):
    """Input schema for LogSentinelTool."""
    tail_lines: int = Field(default=500, description="Number of lines to tail from the log file")

class LogSentinelOutput(BaseModel):
    """Output schema for LogSentinelTool."""
    summary: str = Field(..., description="Summary of the log file")
    last_error: Optional[str] = Field(None, description="Last error found in the log file, if any")
    elapsed: str = Field(..., description="Elapsed time based on first and last timestamp")

class LogSentinelTool(BaseTool[LogSentinelInput, LogSentinelOutput]):
    """
    Tool for tailing, parsing, and summarizing training.log and crash traces.
    """
    
    input_schema = LogSentinelInput
    output_schema = LogSentinelOutput
    
    def _run(self, input_obj: LogSentinelInput) -> LogSentinelOutput:
        """
        Tail the log file, parse it for errors, and compute runtime.
        
        Args:
            input_obj: An instance of LogSentinelInput.
            
        Returns:
            An instance of LogSentinelOutput.
        """
        # Tail the log file
        log_content = self._tail_log(input_obj.tail_lines)
        
        # Parse for errors
        last_error = self._find_last_error(log_content)
        
        # Compute runtime
        elapsed = self._compute_runtime(log_content)
        
        # Generate summary
        summary = self._generate_summary(log_content, last_error, elapsed)
        
        return LogSentinelOutput(
            summary=summary,
            last_error=last_error,
            elapsed=elapsed
        )
    
    def _tail_log(self, tail_lines: int) -> str:
        """
        Tail the log file using the tail command.
        
        Args:
            tail_lines: Number of lines to tail.
            
        Returns:
            The tailed log content as a string.
        """
        try:
            result = subprocess.run(
                ["tail", "-n", str(tail_lines), Paths.LOG],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return f"Error: Could not tail log file {Paths.LOG}"
        except FileNotFoundError:
            return f"Error: Log file {Paths.LOG} not found"
    
    def _find_last_error(self, log_content: str) -> Optional[str]:
        """
        Find the last error in the log content.
        
        Args:
            log_content: The log content to search.
            
        Returns:
            The last error found, or None if no error was found.
        """
        # Regex patterns for different types of errors
        error_patterns = [
            r'Traceback \(most recent call last\):.*?(?=\n\n|\Z)',
            r'RuntimeError:.*?(?=\n\n|\Z)',
            r'AssertionError:.*?(?=\n\n|\Z)',
            r'Error:.*?(?=\n\n|\Z)'
        ]
        
        # Find all errors
        errors = []
        for pattern in error_patterns:
            matches = re.finditer(pattern, log_content, re.DOTALL)
            errors.extend([match.group(0) for match in matches])
        
        # Return the last error, if any
        if errors:
            return errors[-1]
        
        return None
    
    def _compute_runtime(self, log_content: str) -> str:
        """
        Compute the runtime based on the first and last timestamp in the log.
        
        Args:
            log_content: The log content to search.
            
        Returns:
            A string representing the elapsed time.
        """
        # Extract timestamps from the log
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        timestamps = re.findall(timestamp_pattern, log_content)
        
        if len(timestamps) < 2:
            return "Unknown (insufficient timestamps)"
        
        try:
            # Parse the first and last timestamp
            first_time = datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M:%S')
            last_time = datetime.strptime(timestamps[-1], '%Y-%m-%d %H:%M:%S')
            
            # Compute the difference
            delta = last_time - first_time
            
            # Format the elapsed time
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if delta.days > 0:
                return f"{delta.days}d {hours}h {minutes}m {seconds}s"
            elif hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except ValueError:
            return "Unknown (invalid timestamps)"
    
    def _generate_summary(self, log_content: str, last_error: Optional[str], elapsed: str) -> str:
        """
        Generate a summary of the log content.
        
        Args:
            log_content: The log content to summarize.
            last_error: The last error found, if any.
            elapsed: The elapsed time.
            
        Returns:
            A summary of the log content.
        """
        # Count lines
        line_count = log_content.count('\n') + 1
        
        # Count warnings
        warning_count = log_content.lower().count('warning')
        
        # Count errors
        error_count = (
            log_content.lower().count('error') +
            log_content.count('Traceback') +
            log_content.count('Exception')
        )
        
        # Generate summary
        summary = [
            f"Log Summary ({line_count} lines, runtime: {elapsed}):",
            f"- Warnings: {warning_count}",
            f"- Errors: {error_count}"
        ]
        
        # Add error information if available
        if last_error:
            # Truncate error if it's too long
            if len(last_error) > 500:
                last_error = last_error[:497] + "..."
            
            summary.append(f"- Last error: {last_error}")
        else:
            summary.append("- No errors detected")
        
        return "\n".join(summary)