"""
Test Case Generator Service using RAG pipeline.
Generates comprehensive test cases grounded in documentation.
"""

import json
import time
from typing import List, Dict, Any, Optional

from backend.app.utils.logger import init_logger
from backend.app.services.bedrock_client import get_bedrock_client
from backend.app.services.vector_store import get_vector_store

# Initialize logger
logger = init_logger()


class TestCaseGenerator:
    """Generate test cases using RAG pipeline"""

    def __init__(self):
        """Initialize test case generator"""
        self.bedrock_client = get_bedrock_client()
        self.vector_store = get_vector_store()

        logger.info("TestCaseGenerator initialized")

    def generate_test_cases(
        self,
        query: str,
        top_k: int = 5,
        include_positive: bool = True,
        include_negative: bool = True,
        include_edge_cases: bool = True
    ) -> Dict[str, Any]:
        """
        Generate test cases based on query and documentation

        Args:
            query: User query for test case generation
            top_k: Number of relevant documents to retrieve
            include_positive: Include positive test scenarios
            include_negative: Include negative test scenarios
            include_edge_cases: Include edge case scenarios

        Returns:
            Dictionary containing generated test cases
        """
        logger.info(f"Generating test cases for query: {query}")

        logger.log_function_call(
            "generate_test_cases",
            args={
                "query": query[:100],
                "top_k": top_k,
                "include_positive": include_positive,
                "include_negative": include_negative,
                "include_edge_cases": include_edge_cases
            },
            status="started"
        )

        start_time = time.time()

        try:
            # Step 1: Retrieve relevant documentation
            logger.info("Retrieving relevant documentation from vector store")
            relevant_docs = self.vector_store.search(query, top_k=top_k)

            if not relevant_docs:
                logger.warning("No relevant documents found in vector store")
                return {
                    "success": False,
                    "message": "No relevant documentation found. Please build knowledge base first.",
                    "test_cases": []
                }

            # Log retrieved documents
            logger.info(
                f"Retrieved {len(relevant_docs)} relevant documents",
                extra={
                    "doc_sources": [doc['metadata'].get('source_document') for doc in relevant_docs]
                }
            )

            # Step 2: Build context from retrieved documents
            context = self._build_context(relevant_docs)

            # Step 3: Create prompt for LLM
            prompt = self._create_test_case_prompt(
                query=query,
                context=context,
                include_positive=include_positive,
                include_negative=include_negative,
                include_edge_cases=include_edge_cases
            )

            # Step 4: Generate test cases using LLM
            logger.info("Generating test cases using LLM")
            system_prompt = self._get_system_prompt()

            response = self.bedrock_client.invoke_llm(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4000,
                temperature=0.7
            )

            # Step 5: Parse and structure test cases
            test_cases = self._parse_test_cases(response, relevant_docs)

            duration = time.time() - start_time

            logger.log_test_generation(
                test_type="test_cases",
                test_count=len(test_cases),
                duration=duration,
                status="success"
            )

            logger.log_function_call(
                "generate_test_cases",
                args={"test_count": len(test_cases)},
                status="completed"
            )

            return {
                "success": True,
                "message": f"Generated {len(test_cases)} test cases successfully",
                "test_cases": test_cases,
                "sources": [doc['metadata'].get('source_document') for doc in relevant_docs],
                "query": query,
                "generation_time": round(duration, 2)
            }

        except Exception as e:
            logger.log_function_call(
                "generate_test_cases",
                status="failed"
            )
            logger.exception("Error generating test cases")

            return {
                "success": False,
                "message": f"Error generating test cases: {str(e)}",
                "test_cases": []
            }

    def _build_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents"""
        logger.debug("Building context from retrieved documents")

        context_parts = []

        for idx, doc in enumerate(relevant_docs, 1):
            source = doc['metadata'].get('source_document', 'Unknown')
            text = doc['text']
            similarity = doc.get('similarity', 0)

            context_parts.append(
                f"--- Document {idx}: {source} (Relevance: {similarity:.2f}) ---\n{text}\n"
            )

        context = "\n".join(context_parts)

        logger.debug(f"Built context with {len(context)} characters from {len(relevant_docs)} documents")

        return context

    def _get_system_prompt(self) -> str:
        """Get system prompt for test case generation"""
        return """You are an expert QA automation engineer specializing in test case design.
Your task is to generate comprehensive, well-structured test cases based STRICTLY on the provided documentation.

CRITICAL RULES:
1. Base ALL test cases ONLY on information found in the provided documentation
2. DO NOT hallucinate features, fields, or functionality not mentioned in the docs
3. Reference the source document for each test case
4. Generate test cases in structured JSON format
5. Include test_id, feature, scenario, steps, expected_result, and grounded_in fields
6. Make test cases specific, actionable, and testable

Your test cases should be:
- Grounded: Every assertion must be traceable to documentation
- Specific: Clear, unambiguous steps and expected results
- Testable: Can be automated using Selenium or similar tools
- Comprehensive: Cover positive, negative, and edge cases as requested"""

    def _create_test_case_prompt(
        self,
        query: str,
        context: str,
        include_positive: bool,
        include_negative: bool,
        include_edge_cases: bool
    ) -> str:
        """Create prompt for LLM"""
        logger.debug("Creating test case generation prompt")

        test_types = []
        if include_positive:
            test_types.append("positive (happy path)")
        if include_negative:
            test_types.append("negative (error cases)")
        if include_edge_cases:
            test_types.append("edge cases (boundary conditions)")

        test_types_str = ", ".join(test_types)

        prompt = f"""Based on the following documentation, generate comprehensive test cases for: {query}

DOCUMENTATION:
{context}

REQUIREMENTS:
- Generate {test_types_str} test scenarios
- Each test case must include:
  * test_id: Unique identifier (e.g., TC-001, TC-002)
  * feature: Feature being tested
  * test_scenario: Brief description of what is being tested
  * test_type: One of: positive, negative, edge_case
  * preconditions: Required setup before test execution
  * test_steps: Detailed, numbered steps to execute the test
  * expected_result: Expected outcome after executing all steps
  * grounded_in: Source document(s) that support this test case
  * priority: high, medium, or low
  * test_data: Specific test data to use (if applicable)

- Ensure ALL test cases are grounded in the provided documentation
- DO NOT invent features or functionality not described in the docs
- Be specific about element IDs, field names, and values mentioned in documentation
- Make steps clear enough for automation

OUTPUT FORMAT:
Provide your response as a valid JSON array of test case objects.

Example format:
[
  {{
    "test_id": "TC-001",
    "feature": "Discount Code Application",
    "test_scenario": "Apply valid discount code SAVE15",
    "test_type": "positive",
    "preconditions": ["Cart contains at least one item"],
    "test_steps": [
      "Navigate to checkout page",
      "Add items to cart",
      "Enter discount code 'SAVE15' in the discount code field",
      "Click 'Apply Code' button"
    ],
    "expected_result": "Discount of 15% applied to subtotal, success message displayed",
    "grounded_in": "product_specs.md - Section 3.1: Valid discount codes include SAVE15 with 15% discount",
    "priority": "high",
    "test_data": {{
      "discount_code": "SAVE15",
      "expected_discount_percentage": 15
    }}
  }}
]

Generate comprehensive test cases now:"""

        return prompt

    def _parse_test_cases(
        self,
        llm_response: str,
        relevant_docs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse LLM response into structured test cases"""
        logger.debug("Parsing LLM response into structured test cases")

        try:
            # Try to extract JSON from response
            # Sometimes LLM wraps JSON in markdown code blocks
            response = llm_response.strip()

            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]

            if response.endswith("```"):
                response = response[:-3]

            response = response.strip()

            # Parse JSON
            test_cases = json.loads(response)

            # Validate it's a list
            if not isinstance(test_cases, list):
                logger.warning("LLM response is not a list, wrapping in list")
                test_cases = [test_cases]

            logger.info(f"Successfully parsed {len(test_cases)} test cases")

            # Add metadata
            for test_case in test_cases:
                if 'metadata' not in test_case:
                    test_case['metadata'] = {
                        'source_documents': [doc['metadata'].get('source_document') for doc in relevant_docs]
                    }

            return test_cases

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
            logger.debug(f"LLM Response: {llm_response[:500]}")

            # Return raw response wrapped in a test case
            return [{
                "test_id": "TC-ERROR",
                "feature": "Parse Error",
                "test_scenario": "Failed to parse test cases",
                "raw_response": llm_response,
                "error": str(e)
            }]

        except Exception as e:
            logger.exception("Unexpected error parsing test cases")
            return [{
                "test_id": "TC-ERROR",
                "error": str(e),
                "raw_response": llm_response
            }]

    def generate_all_test_cases(self) -> Dict[str, Any]:
        """Generate comprehensive test cases for all features"""
        logger.info("Generating comprehensive test cases for all features")

        queries = [
            "Generate test cases for discount code functionality",
            "Generate test cases for form validation (name, email, address)",
            "Generate test cases for shopping cart operations (add, remove, modify quantity)",
            "Generate test cases for shipping method selection",
            "Generate test cases for payment method selection",
            "Generate test cases for order submission and checkout flow",
        ]

        all_test_cases = []

        for query in queries:
            result = self.generate_test_cases(query, top_k=5)
            if result['success']:
                all_test_cases.extend(result['test_cases'])

        logger.info(f"Generated {len(all_test_cases)} total test cases")

        return {
            "success": True,
            "message": f"Generated {len(all_test_cases)} test cases",
            "test_cases": all_test_cases
        }


# Global instance
_test_case_generator = None


def get_test_case_generator() -> TestCaseGenerator:
    """Get or create global test case generator instance"""
    global _test_case_generator
    if _test_case_generator is None:
        _test_case_generator = TestCaseGenerator()
    return _test_case_generator
