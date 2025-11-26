#!/usr/bin/env python3
"""
Comprehensive test script for QA Agent setup and functionality
"""

import sys
import os
from pathlib import Path

# Test results tracking
tests_passed = 0
tests_failed = 0
test_results = []

def test(name, func):
    """Run a test and track results"""
    global tests_passed, tests_failed
    try:
        print(f"\n🧪 Testing: {name}")
        func()
        print(f"   ✅ PASS")
        tests_passed += 1
        test_results.append((name, "PASS", None))
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
        tests_failed += 1
        test_results.append((name, "FAIL", str(e)))
        return False


def test_python_version():
    """Test Python version >= 3.9"""
    version = sys.version_info
    assert version.major == 3 and version.minor >= 9, \
        f"Python 3.9+ required, found {version.major}.{version.minor}"
    print(f"   Python version: {version.major}.{version.minor}.{version.micro}")
    if version.minor < 10:
        print(f"   ⚠️  Python 3.10+ recommended, but 3.9 should work")


def test_project_structure():
    """Test that all required directories and files exist"""
    required_paths = [
        'backend/app/main.py',
        'backend/app/models.py',
        'backend/app/services/bedrock_client.py',
        'backend/app/services/document_parser.py',
        'backend/app/services/vector_store.py',
        'backend/app/services/test_case_generator.py',
        'backend/app/services/selenium_generator.py',
        'backend/app/utils/logger.py',
        'backend/config.py',
        'frontend/streamlit_app.py',
        'project_assets/checkout.html',
        'project_assets/support_docs/product_specs.md',
        'project_assets/support_docs/ui_ux_guide.txt',
        'project_assets/support_docs/api_endpoints.json',
        'project_assets/support_docs/business_rules.md',
        'project_assets/support_docs/test_data.json',
        'requirements.txt',
        '.env.example',
        'README.md',
        'QUICKSTART.md',
    ]

    missing = []
    for path in required_paths:
        if not Path(path).exists():
            missing.append(path)

    assert not missing, f"Missing files: {', '.join(missing)}"
    print(f"   All {len(required_paths)} required files present")


def test_dependencies():
    """Test that all required packages can be imported"""
    required_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('streamlit', 'Streamlit'),
        ('boto3', 'Boto3'),
        ('faiss', 'FAISS'),
        ('pydantic', 'Pydantic'),
        ('numpy', 'NumPy'),
        ('loguru', 'Loguru'),
    ]

    missing = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"   ✓ {name}")
        except ImportError:
            missing.append(name)
            print(f"   ✗ {name}")

    if missing:
        raise ImportError(
            f"Missing packages: {', '.join(missing)}. "
            f"Run: pip install -r requirements.txt"
        )


def test_backend_imports():
    """Test that backend modules can be imported"""
    sys.path.insert(0, str(Path.cwd()))

    modules = [
        'backend.config',
        'backend.app.models',
        'backend.app.utils.logger',
    ]

    for module in modules:
        __import__(module)
        print(f"   ✓ {module}")


def test_environment_file():
    """Test .env.example exists and has required variables"""
    env_example = Path('.env.example')
    assert env_example.exists(), ".env.example file not found"

    content = env_example.read_text()

    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'BEDROCK_LLM_MODEL_ID',
        'BEDROCK_EMBEDDING_MODEL_ID',
    ]

    missing = []
    for var in required_vars:
        if var not in content:
            missing.append(var)

    assert not missing, f"Missing env vars in .env.example: {', '.join(missing)}"
    print(f"   All {len(required_vars)} required environment variables defined")


def test_project_assets():
    """Test that project assets are valid"""
    # Test checkout.html
    checkout_html = Path('project_assets/checkout.html')
    html_content = checkout_html.read_text()

    # Check for key elements
    required_elements = [
        'add-laptop',
        'add-headphones',
        'add-keyboard',
        'discount-code',
        'apply-discount',
        'name',
        'email',
        'address',
        'standard-shipping',
        'express-shipping',
        'credit-card',
        'paypal',
        'pay-now',
    ]

    missing_elements = []
    for element_id in required_elements:
        if f'id="{element_id}"' not in html_content:
            missing_elements.append(element_id)

    assert not missing_elements, \
        f"Missing elements in checkout.html: {', '.join(missing_elements)}"

    print(f"   ✓ checkout.html has all {len(required_elements)} required elements")

    # Test support docs
    import json

    # Test JSON files are valid
    json_files = [
        'project_assets/support_docs/api_endpoints.json',
        'project_assets/support_docs/test_data.json',
    ]

    for json_file in json_files:
        with open(json_file) as f:
            data = json.load(f)
        print(f"   ✓ {Path(json_file).name} is valid JSON")

    # Check markdown files have content
    md_files = [
        'project_assets/support_docs/product_specs.md',
        'project_assets/support_docs/business_rules.md',
    ]

    for md_file in md_files:
        content = Path(md_file).read_text()
        assert len(content) > 100, f"{md_file} seems too short"
        print(f"   ✓ {Path(md_file).name} has content ({len(content)} chars)")


def test_configuration():
    """Test configuration module"""
    from backend.config import settings

    # Check that settings object exists and has required attributes
    required_attrs = [
        'aws_region',
        'bedrock_llm_model_id',
        'bedrock_embedding_model_id',
        'chunk_size',
        'chunk_overlap',
        'vector_db_path',
    ]

    for attr in required_attrs:
        assert hasattr(settings, attr), f"Settings missing attribute: {attr}"
        print(f"   ✓ settings.{attr} = {getattr(settings, attr)}")


def test_logger():
    """Test logger initialization"""
    from backend.app.utils.logger import init_logger

    logger = init_logger()
    assert logger is not None, "Logger initialization failed"

    # Test logging methods
    logger.info("Test log message")
    logger.debug("Test debug message")

    print("   ✓ Logger initialized and working")


def test_document_parser():
    """Test document parser"""
    from backend.app.services.document_parser import get_document_parser

    parser = get_document_parser()

    # Test parsing a markdown file
    md_file = 'project_assets/support_docs/product_specs.md'
    chunks = parser.parse_file(md_file)

    assert len(chunks) > 0, "No chunks created from markdown file"
    assert chunks[0].text, "Chunk has no text"
    assert chunks[0].metadata, "Chunk has no metadata"

    print(f"   ✓ Parsed {md_file}")
    print(f"   ✓ Created {len(chunks)} chunks")
    print(f"   ✓ First chunk: {len(chunks[0].text)} chars")


def test_documentation():
    """Test that documentation exists and is comprehensive"""
    readme = Path('README.md').read_text()

    # Check for key sections
    required_sections = [
        'Prerequisites',
        'Installation',
        'Configuration',
        'Usage',
        'API Documentation',
        'Deployment',
        'Troubleshooting',
    ]

    missing = []
    for section in required_sections:
        if section.lower() not in readme.lower():
            missing.append(section)

    assert not missing, f"README missing sections: {', '.join(missing)}"

    print(f"   ✓ README.md has all required sections")
    print(f"   ✓ README.md is {len(readme)} characters")

    # Check QUICKSTART exists
    quickstart = Path('QUICKSTART.md')
    assert quickstart.exists(), "QUICKSTART.md not found"
    print(f"   ✓ QUICKSTART.md exists ({len(quickstart.read_text())} chars)")


def print_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    total = tests_passed + tests_failed
    percentage = (tests_passed / total * 100) if total > 0 else 0

    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"Success Rate: {percentage:.1f}%")

    if tests_failed > 0:
        print("\n" + "="*70)
        print("FAILED TESTS")
        print("="*70)
        for name, status, error in test_results:
            if status == "FAIL":
                print(f"\n❌ {name}")
                print(f"   Error: {error}")

    print("\n" + "="*70)

    if tests_failed == 0:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ The QA Agent is properly set up and ready to run!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env: cp .env.example .env")
        print("2. Add your AWS credentials to .env")
        print("3. Run: ./start.sh")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nPlease fix the issues above before running the application.")

    print("="*70 + "\n")


def main():
    """Run all tests"""
    print("="*70)
    print("QA AGENT - SETUP TEST SUITE")
    print("="*70)
    print(f"Working directory: {Path.cwd()}")
    print(f"Python: {sys.version}")

    # Run tests in order
    test("Python Version Check", test_python_version)
    test("Project Structure", test_project_structure)
    test("Dependencies Installation", test_dependencies)
    test("Backend Module Imports", test_backend_imports)
    test("Environment Configuration", test_environment_file)
    test("Project Assets Validation", test_project_assets)
    test("Configuration Module", test_configuration)
    test("Logger Initialization", test_logger)
    test("Document Parser", test_document_parser)
    test("Documentation Completeness", test_documentation)

    # Print summary
    print_summary()

    # Return exit code
    return 0 if tests_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
