"""
CreedAuditTool - Static-analyzes changed files looking for forbidden patterns.
"""

import os
import re
from typing import List, Dict, Pattern
from pydantic import BaseModel, Field

from .base_tool import BaseTool

class CreedAuditInput(BaseModel):
    """Input schema for CreedAuditTool."""
    files: List[str] = Field(..., description="List of files to audit")

class CreedAuditOutput(BaseModel):
    """Output schema for CreedAuditTool."""
    violations: List[str] = Field(default_factory=list, description="List of creed violations found")

class CreedAuditTool(BaseTool[CreedAuditInput, CreedAuditOutput]):
    """
    Tool for static-analyzing changed files looking for forbidden patterns.
    """
    
    input_schema = CreedAuditInput
    output_schema = CreedAuditOutput
    
    def __init__(self):
        """Initialize the tool with forbidden patterns."""
        super().__init__()
        
        # Compile forbidden patterns once
        self.forbidden_patterns: Dict[str, Pattern] = {
            "is_none": re.compile(r'\bis\s+None\b'),
            "is_not_none": re.compile(r'\bis\s+not\s+None\b'),
            "kwargs": re.compile(r'\*\*kwargs'),
            "mock": re.compile(r'\bmock\b|\bMagicMock\b'),
            "if_none_fallback": re.compile(r'if\s+.*?is\s+None'),
            "hasattr": re.compile(r'\bhasattr\b'),
            "silent_exception": re.compile(r'except.*?:(\s*)pass'),
            "unused_tensor": re.compile(r'torch\.tensor\(.*?\).*?(?!\S)'),
            "fallback_pattern": re.compile(r'if\s+.*?:\s*.*?\s*else\s*.*?return\s+0'),
        }
    
    def _run(self, input_obj: CreedAuditInput) -> CreedAuditOutput:
        """
        Audit the specified files for creed violations.
        
        Args:
            input_obj: An instance of CreedAuditInput.
            
        Returns:
            An instance of CreedAuditOutput.
        """
        violations = []
        
        for file_path in input_obj.files:
            # Skip files that don't exist
            if not os.path.exists(file_path):
                violations.append(f"File not found: {file_path}")
                continue
            
            # Skip non-Python files
            if not file_path.endswith(('.py', '.pyx', '.pyi')):
                continue
            
            # Read the file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                violations.append(f"Error reading {file_path}: {str(e)}")
                continue
            
            # Check for violations
            file_violations = self._check_violations(file_path, content)
            violations.extend(file_violations)
        
        return CreedAuditOutput(violations=violations)
    
    def _check_violations(self, file_path: str, content: str) -> List[str]:
        """
        Check the content for creed violations.
        
        Args:
            file_path: The path of the file being checked.
            content: The content of the file.
            
        Returns:
            A list of violation messages.
        """
        violations = []
        
        # Split content into lines for better error reporting
        lines = content.split('\n')
        
        for pattern_name, pattern in self.forbidden_patterns.items():
            # Find all matches
            for i, line in enumerate(lines):
                if pattern.search(line):
                    # Skip comments
                    if line.strip().startswith('#'):
                        continue
                    
                    # Generate violation message
                    violation_msg = self._format_violation(file_path, i+1, line, pattern_name)
                    violations.append(violation_msg)
        
        return violations
    
    def _format_violation(self, file_path: str, line_num: int, line: str, pattern_name: str) -> str:
        """
        Format a violation message.
        
        Args:
            file_path: The path of the file with the violation.
            line_num: The line number of the violation.
            line: The line content.
            pattern_name: The name of the violated pattern.
            
        Returns:
            A formatted violation message.
        """
        # Trim the line if it's too long
        if len(line) > 50:
            line = line[:47] + "..."
        
        # Map pattern names to human-readable descriptions
        pattern_descriptions = {
            "is_none": "Using 'is None' check (forbidden by Creed)",
            "is_not_none": "Using 'is not None' check (forbidden by Creed)",
            "kwargs": "Using '**kwargs' (forbidden by Creed)",
            "mock": "Using mock objects (forbidden by Creed)",
            "if_none_fallback": "Using None fallback pattern (forbidden by Creed)",
            "hasattr": "Using hasattr() (forbidden by Creed)",
            "silent_exception": "Silent exception handling (forbidden by Creed)",
            "unused_tensor": "Potentially unused tensor (forbidden by Creed)",
            "fallback_pattern": "Using fallback pattern (forbidden by Creed)",
        }
        
        description = pattern_descriptions.get(pattern_name, f"Violation of {pattern_name}")
        
        return f"{file_path}:{line_num}: {description}\n  {line.strip()}"