"""
Selenium Script Generator Service.
Converts test cases into executable Python Selenium scripts.
"""

import time
from typing import Dict, Any, Optional
from pathlib import Path

from backend.app.utils.logger import init_logger
from backend.app.services.bedrock_client import get_bedrock_client
from backend.app.services.vector_store import get_vector_store

# Initialize logger
logger = init_logger()


class SeleniumScriptGenerator:
    """Generate Selenium Python scripts from test cases"""

    def __init__(self):
        """Initialize Selenium script generator"""
        self.bedrock_client = get_bedrock_client()
        self.vector_store = get_vector_store()

        logger.info("SeleniumScriptGenerator initialized")

    def generate_selenium_script(
        self,
        test_case: Dict[str, Any],
        html_content: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Generate Selenium Python script from test case

        Args:
            test_case: Test case dictionary
            html_content: HTML content of the page to test
            top_k: Number of relevant documents to retrieve for context

        Returns:
            Dictionary containing generated script and metadata
        """
        logger.info(f"Generating Selenium script for test case: {test_case.get('test_id', 'Unknown')}")

        logger.log_function_call(
            "generate_selenium_script",
            args={
                "test_id": test_case.get('test_id'),
                "feature": test_case.get('feature')
            },
            status="started"
        )

        start_time = time.time()

        try:
            # Step 1: Retrieve relevant documentation
            query = f"{test_case.get('feature', '')} {test_case.get('test_scenario', '')}"
            logger.info(f"Retrieving documentation for: {query}")

            relevant_docs = self.vector_store.search(query, top_k=top_k)

            # Step 2: Build context
            context = self._build_context(relevant_docs, html_content)

            # Step 3: Create prompt
            prompt = self._create_selenium_prompt(test_case, context, html_content)

            # Step 4: Generate script using LLM
            logger.info("Generating Selenium script using LLM")
            system_prompt = self._get_system_prompt()

            response = self.bedrock_client.invoke_llm(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=3000,
                temperature=0.5  # Lower temperature for code generation
            )

            # Step 5: Extract and clean script
            script = self._extract_script(response)

            duration = time.time() - start_time

            logger.log_test_generation(
                test_type="selenium_script",
                duration=duration,
                status="success"
            )

            logger.log_function_call(
                "generate_selenium_script",
                args={"test_id": test_case.get('test_id')},
                status="completed"
            )

            return {
                "success": True,
                "message": "Selenium script generated successfully",
                "script": script,
                "test_id": test_case.get('test_id'),
                "feature": test_case.get('feature'),
                "generation_time": round(duration, 2),
                "sources": [doc['metadata'].get('source_document') for doc in relevant_docs]
            }

        except Exception as e:
            logger.log_function_call(
                "generate_selenium_script",
                status="failed"
            )
            logger.exception("Error generating Selenium script")

            return {
                "success": False,
                "message": f"Error generating script: {str(e)}",
                "script": None
            }

    def _build_context(
        self,
        relevant_docs: list,
        html_content: Optional[str]
    ) -> str:
        """Build context from documentation and HTML"""
        logger.debug("Building context for Selenium script generation")

        context_parts = []

        # Add documentation context
        for idx, doc in enumerate(relevant_docs, 1):
            source = doc['metadata'].get('source_document', 'Unknown')
            text = doc['text']

            context_parts.append(f"--- Documentation {idx}: {source} ---\n{text}\n")

        # Add HTML context if provided
        if html_content:
            # Limit HTML content size
            html_snippet = html_content[:5000] if len(html_content) > 5000 else html_content
            context_parts.append(f"--- HTML Structure ---\n{html_snippet}\n")

        context = "\n".join(context_parts)

        logger.debug(f"Built context with {len(context)} characters")

        return context

    def _get_system_prompt(self) -> str:
        """Get system prompt for Selenium script generation"""
        return """You are an expert Selenium automation engineer specializing in Python test automation.
Your task is to generate high-quality, production-ready Selenium Python scripts.

CRITICAL RULES:
1. Generate ONLY valid, executable Python code
2. Use proper Selenium WebDriver syntax for Python
3. Base selectors on the actual HTML structure provided
4. Include proper waits (WebDriverWait, expected_conditions)
5. Add error handling and assertions
6. Follow Python best practices and PEP 8 style
7. Add clear comments explaining each step
8. Use pytest or unittest framework
9. Include setup and teardown methods
10. Make the code production-ready and maintainable

Your script should:
- Import necessary modules (selenium, pytest/unittest, time, etc.)
- Include a test class with setup and teardown
- Implement the test case steps as described
- Use explicit waits instead of time.sleep()
- Have proper assertions matching expected results
- Include logging for debugging
- Handle potential exceptions gracefully"""

    def _create_selenium_prompt(
        self,
        test_case: Dict[str, Any],
        context: str,
        html_content: Optional[str]
    ) -> str:
        """Create prompt for Selenium script generation"""
        logger.debug("Creating Selenium script generation prompt")

        # Extract test case details
        test_id = test_case.get('test_id', 'TC-UNKNOWN')
        feature = test_case.get('feature', 'Unknown Feature')
        scenario = test_case.get('test_scenario', 'Unknown Scenario')
        steps = test_case.get('test_steps', [])
        expected_result = test_case.get('expected_result', 'Unknown')
        test_data = test_case.get('test_data', {})

        # Format steps
        steps_str = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])

        prompt = f"""Generate a complete, executable Selenium Python script for the following test case.

TEST CASE DETAILS:
Test ID: {test_id}
Feature: {feature}
Scenario: {scenario}

PRECONDITIONS:
{test_case.get('preconditions', ['None'])}

TEST STEPS:
{steps_str}

EXPECTED RESULT:
{expected_result}

TEST DATA:
{test_data if test_data else 'Use data from context'}

CONTEXT (Documentation and HTML):
{context}

REQUIREMENTS:
1. Create a complete Python test script using pytest framework
2. Include proper imports (selenium, pytest, webdriver_manager, etc.)
3. Use the actual element IDs, names, and CSS selectors from the HTML provided
4. Implement explicit waits (WebDriverWait with expected_conditions)
5. Add assertions to verify the expected result
6. Include setup method to initialize WebDriver
7. Include teardown method to close WebDriver
8. Add comments explaining each step
9. Handle potential exceptions
10. Make the script ready to run with: pytest <script_name>.py

IMPORTANT:
- Use WebDriver for Chrome with webdriver_manager for automatic driver management
- All selectors MUST match the actual HTML structure provided
- Include time.sleep() only where absolutely necessary, prefer explicit waits
- Add screenshots on failure for debugging
- Log all major actions

Generate the complete Selenium Python script now:"""

        return prompt

    def _extract_script(self, llm_response: str) -> str:
        """Extract Python script from LLM response"""
        logger.debug("Extracting Python script from LLM response")

        try:
            response = llm_response.strip()

            # Remove markdown code blocks if present
            if "```python" in response:
                # Extract code between ```python and ```
                start = response.find("```python") + 9
                end = response.find("```", start)
                if end != -1:
                    script = response[start:end].strip()
                else:
                    script = response[start:].strip()
            elif "```" in response:
                # Extract code between ``` and ```
                start = response.find("```") + 3
                end = response.find("```", start)
                if end != -1:
                    script = response[start:end].strip()
                else:
                    script = response[start:].strip()
            else:
                # No code blocks, use entire response
                script = response

            logger.info(f"Extracted Selenium script with {len(script)} characters")

            return script

        except Exception as e:
            logger.error(f"Error extracting script: {str(e)}")
            return llm_response

    def save_script(
        self,
        script: str,
        test_id: str,
        output_dir: Optional[str] = None
    ) -> str:
        """
        Save Selenium script to file

        Args:
            script: Python script content
            test_id: Test case ID
            output_dir: Output directory path

        Returns:
            Path to saved script file
        """
        logger.info(f"Saving Selenium script for test {test_id}")

        try:
            from backend.config import settings

            # Determine output directory
            if output_dir is None:
                output_dir = settings.generated_scripts_path

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Create filename
            filename = f"test_{test_id.lower().replace('-', '_')}.py"
            file_path = output_path / filename

            # Save script
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(script)

            logger.info(f"Selenium script saved to: {file_path}")

            return str(file_path)

        except Exception as e:
            logger.error(f"Error saving script: {str(e)}")
            raise

    def generate_and_save_script(
        self,
        test_case: Dict[str, Any],
        html_content: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate and save Selenium script

        Args:
            test_case: Test case dictionary
            html_content: HTML content
            output_dir: Output directory

        Returns:
            Result dictionary with script path
        """
        logger.info(f"Generating and saving script for test: {test_case.get('test_id')}")

        try:
            # Generate script
            result = self.generate_selenium_script(test_case, html_content)

            if not result['success']:
                return result

            # Save script
            test_id = test_case.get('test_id', 'unknown')
            file_path = self.save_script(result['script'], test_id, output_dir)

            result['file_path'] = file_path

            logger.info(f"Script generated and saved successfully: {file_path}")

            return result

        except Exception as e:
            logger.exception("Error generating and saving script")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "script": None
            }


# Global instance
_selenium_generator = None


def get_selenium_generator() -> SeleniumScriptGenerator:
    """Get or create global Selenium script generator instance"""
    global _selenium_generator
    if _selenium_generator is None:
        _selenium_generator = SeleniumScriptGenerator()
    return _selenium_generator
