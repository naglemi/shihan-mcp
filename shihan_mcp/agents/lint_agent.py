"""
LintAgent - Optional static-analysis LLM for catching subtle tensor mishandling.

This is a placeholder for the future extension mentioned in the shihan_creation.txt.
"""

import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import openai

from ..config import ChatCfg

class LintInput(BaseModel):
    """Input schema for LintAgent."""
    file_path: str = Field(..., description="Path to the file to lint")
    code: Optional[str] = Field(None, description="Code to lint (if not provided, will read from file_path)")

class LintIssue(BaseModel):
    """Schema for a lint issue."""
    line: int = Field(..., description="Line number where the issue was found")
    column: Optional[int] = Field(None, description="Column number where the issue was found")
    message: str = Field(..., description="Description of the issue")
    severity: str = Field(..., description="Severity of the issue (error, warning, info)")

class LintOutput(BaseModel):
    """Output schema for LintAgent."""
    issues: List[LintIssue] = Field(default_factory=list, description="List of lint issues found")
    summary: str = Field(..., description="Summary of the linting results")

class LintAgent:
    """
    Agent for static-analysis of code to catch subtle tensor mishandling.
    
    This is a placeholder for the future extension mentioned in the shihan_creation.txt.
    """
    
    def __init__(self):
        """Initialize the lint agent."""
        pass
    
    def run(self, input_obj: LintInput) -> LintOutput:
        """
        Run the lint agent on the specified file or code.
        
        Args:
            input_obj: An instance of LintInput.
            
        Returns:
            An instance of LintOutput.
        """
        # Get the code to lint
        code = input_obj.code
        if code is None:
            # Read the code from the file
            try:
                with open(input_obj.file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            except Exception as e:
                return LintOutput(
                    issues=[],
                    summary=f"Error reading file: {str(e)}"
                )
        
        # Check if the file is a Python file
        if not input_obj.file_path.endswith('.py'):
            return LintOutput(
                issues=[],
                summary="Not a Python file, skipping lint"
            )
        
        # Check if the file contains tensor operations
        if 'torch' not in code and 'tensorflow' not in code and 'np.array' not in code:
            return LintOutput(
                issues=[],
                summary="No tensor operations found, skipping lint"
            )
        
        # This is where the actual linting would happen
        # For now, just return a placeholder message
        return LintOutput(
            issues=[],
            summary="LintAgent is a placeholder for a future extension. It will use an LLM to catch subtle tensor mishandling."
        )
    
    def _lint_with_llm(self, code: str, file_path: str) -> List[LintIssue]:
        """
        Use an LLM to lint the code.
        
        Args:
            code: The code to lint.
            file_path: The path of the file being linted.
            
        Returns:
            A list of lint issues.
        """
        # Check if API key is available
        if not ChatCfg.api_key:
            return []
        
        try:
            # Create OpenAI client
            client = openai.OpenAI(api_key=ChatCfg.api_key)
            
            # Prepare the system prompt
            system_prompt = """
            You are a Python code linter specialized in tensor operations. Your task is to analyze the code and identify issues
            related to tensor handling, such as:
            
            1. Dimension mismatches
            2. Incorrect broadcasting
            3. Inefficient operations
            4. Memory leaks
            5. Potential numerical instability
            6. Unused tensors
            
            For each issue, provide:
            1. The line number
            2. A description of the issue
            3. The severity (error, warning, info)
            
            Your output must be in the following JSON format:
            [
                {
                    "line": <line_number>,
                    "column": <column_number or null>,
                    "message": "<description of the issue>",
                    "severity": "<error|warning|info>"
                },
                ...
            ]
            """
            
            # Prepare the user prompt
            user_prompt = f"Here is the code to lint from {file_path}:\n\n{code}"
            
            # Call the OpenAI API
            response = client.chat.completions.create(
                model=ChatCfg.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=ChatCfg.max_tokens,
                temperature=0.2,  # Low temperature for more consistent results
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            lint_result = response.choices[0].message.content
            
            # Convert the JSON string to a Python list
            import json
            lint_issues = json.loads(lint_result)
            
            # Convert to LintIssue objects
            return [LintIssue(**issue) for issue in lint_issues]
            
        except Exception as e:
            return [
                LintIssue(
                    line=1,
                    message=f"Error linting code: {str(e)}",
                    severity="error"
                )
            ]