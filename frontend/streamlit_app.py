"""
Streamlit UI for QA Agent - Test Case and Script Generator
"""

import os
import json
import requests
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="QA Agent - Test Case Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .test-case-card {
        border: 2px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    """Check if API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_documents(files) -> Dict[str, Any]:
    """Upload documents to API"""
    try:
        files_data = [
            ("files", (file.name, file.getvalue(), file.type))
            for file in files
        ]

        response = requests.post(
            f"{API_BASE_URL}/api/upload-documents",
            files=files_data
        )

        return response.json()

    except Exception as e:
        return {"success": False, "message": str(e)}


def build_knowledge_base(file_paths: List[str], clear_existing: bool = True) -> Dict[str, Any]:
    """Build knowledge base from uploaded documents"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/build-knowledge-base",
            json={
                "clear_existing": clear_existing,
                "file_paths": file_paths
            }
        )

        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        else:
            # Handle error response
            error_data = response.json()
            error_message = error_data.get('detail', str(error_data))
            return {"success": False, "message": error_message}

    except Exception as e:
        return {"success": False, "message": str(e)}


def get_kb_stats() -> Dict[str, Any]:
    """Get knowledge base statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge-base/stats")

        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            error_message = error_data.get('detail', str(error_data))
            return {"success": False, "message": error_message}

    except Exception as e:
        return {"success": False, "message": str(e)}


def generate_test_cases(
    query: str,
    top_k: int = 5,
    include_positive: bool = True,
    include_negative: bool = True,
    include_edge_cases: bool = True
) -> Dict[str, Any]:
    """Generate test cases"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generate-test-cases",
            json={
                "query": query,
                "top_k": top_k,
                "include_positive": include_positive,
                "include_negative": include_negative,
                "include_edge_cases": include_edge_cases
            }
        )

        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            error_message = error_data.get('detail', str(error_data))
            return {"success": False, "message": error_message}

    except Exception as e:
        return {"success": False, "message": str(e)}


def generate_all_test_cases() -> Dict[str, Any]:
    """Generate all test cases"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/generate-all-test-cases")

        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            error_message = error_data.get('detail', str(error_data))
            return {"success": False, "message": error_message}

    except Exception as e:
        return {"success": False, "message": str(e)}


def generate_selenium_script(
    test_case: Dict[str, Any],
    html_content: str = None,
    save_to_file: bool = False
) -> Dict[str, Any]:
    """Generate Selenium script"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generate-selenium-script",
            json={
                "test_case": test_case,
                "html_content": html_content,
                "save_to_file": save_to_file
            }
        )

        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            error_message = error_data.get('detail', str(error_data))
            return {"success": False, "message": error_message}

    except Exception as e:
        return {"success": False, "message": str(e)}


def display_test_case(test_case: Dict[str, Any], index: int):
    """Display a single test case"""
    test_id = test_case.get('test_id', f'TC-{index}')
    feature = test_case.get('feature', 'Unknown')
    scenario = test_case.get('test_scenario', 'Unknown')
    test_type = test_case.get('test_type', 'unknown')
    priority = test_case.get('priority', 'medium')

    with st.expander(f"**{test_id}** - {feature}: {scenario}", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"**Type:** {test_type}")
        with col2:
            st.markdown(f"**Priority:** {priority}")
        with col3:
            if test_case.get('grounded_in'):
                st.markdown(f"**Source:** {test_case['grounded_in'][:50]}...")

        if test_case.get('preconditions'):
            st.markdown("**Preconditions:**")
            for precond in test_case['preconditions']:
                st.markdown(f"- {precond}")

        if test_case.get('test_steps'):
            st.markdown("**Test Steps:**")
            for i, step in enumerate(test_case['test_steps'], 1):
                st.markdown(f"{i}. {step}")

        if test_case.get('expected_result'):
            st.markdown(f"**Expected Result:** {test_case['expected_result']}")

        if test_case.get('test_data'):
            st.markdown("**Test Data:**")
            st.json(test_case['test_data'])

        # Button to generate Selenium script for this test case
        if st.button(f"Generate Selenium Script", key=f"gen_selenium_{test_id}_{index}"):
            st.session_state[f'selected_test_case_{index}'] = test_case
            st.session_state['show_selenium_generator'] = True
            st.rerun()


def main():
    """Main Streamlit application"""

    # Header
    st.markdown('<div class="main-header">🤖 QA Agent - Test Case & Script Generator</div>', unsafe_allow_html=True)

    # Check API health
    if not check_api_health():
        st.markdown(
            '<div class="error-box">⚠️ Cannot connect to API. Please ensure the backend is running on '
            f'{API_BASE_URL}</div>',
            unsafe_allow_html=True
        )
        st.stop()

    # Sidebar
    with st.sidebar:
        st.header("📊 Navigation")

        page = st.radio(
            "Go to",
            [
                "🏠 Home",
                "📁 Upload Documents",
                "🧠 Build Knowledge Base",
                "✍️ Generate Test Cases",
                "🔧 Generate Selenium Scripts",
                "📈 Statistics"
            ]
        )

        st.markdown("---")

        # Display knowledge base stats
        st.subheader("Knowledge Base Info")
        try:
            stats_result = get_kb_stats()
            if stats_result.get('success'):
                stats = stats_result.get('stats', {})
                st.metric("Documents", stats.get('num_documents', 0))
                st.metric("Collection", stats.get('collection_name', 'N/A'))
        except:
            st.info("Stats unavailable")

    # Main content based on selected page
    if "Home" in page:
        show_home_page()

    elif "Upload Documents" in page:
        show_upload_page()

    elif "Build Knowledge Base" in page:
        show_build_kb_page()

    elif "Generate Test Cases" in page:
        show_generate_test_cases_page()

    elif "Generate Selenium Scripts" in page:
        show_selenium_generator_page()

    elif "Statistics" in page:
        show_statistics_page()


def show_home_page():
    """Home page"""
    st.markdown("### Welcome to QA Agent!")

    st.markdown("""
    This tool helps you generate comprehensive test cases and Selenium automation scripts
    based on your project documentation.

    **Getting Started:**

    1. **📁 Upload Documents**: Upload your support documents (product specs, UI/UX guides, API docs, etc.)
    2. **🧠 Build Knowledge Base**: Process documents and build the AI knowledge base
    3. **✍️ Generate Test Cases**: Create test cases grounded in your documentation
    4. **🔧 Generate Selenium Scripts**: Convert test cases into executable Selenium Python scripts

    **Supported Document Formats:**
    - Markdown (.md)
    - Text files (.txt)
    - JSON (.json)
    - PDF (.pdf)
    - HTML (.html)
    - Word Documents (.docx, .doc)

    **Features:**
    - 🤖 Autonomous test case generation using AWS Bedrock (Nova Lite)
    - 📚 RAG-based approach for documentation-grounded testing
    - 🎯 Zero hallucination - all test cases based strictly on provided docs
    - 🔧 Automated Selenium script generation
    - 📊 Comprehensive logging and statistics
    """)

    st.markdown('<div class="info-box">💡 Tip: Start by uploading your project documentation!</div>', unsafe_allow_html=True)


def show_upload_page():
    """Upload documents page"""
    st.markdown("### 📁 Upload Support Documents")

    st.markdown("""
    Upload your project documentation files. These will be processed to build the knowledge base
    for test case generation.
    """)

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        accept_multiple_files=True,
        type=['md', 'txt', 'json', 'pdf', 'html', 'docx', 'doc']
    )

    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")

        for file in uploaded_files:
            st.markdown(f"- {file.name} ({file.size} bytes)")

        if st.button("Upload Files", type="primary"):
            with st.spinner("Uploading files..."):
                result = upload_documents(uploaded_files)

            if result.get('success'):
                st.markdown(
                    f'<div class="success-box">✅ {result["message"]}</div>',
                    unsafe_allow_html=True
                )
                st.session_state['uploaded_file_paths'] = result.get('file_paths', [])

                # Display uploaded files
                st.markdown("**Uploaded Files:**")
                for filename in result.get('files', []):
                    st.markdown(f"- {filename}")

            else:
                st.markdown(
                    f'<div class="error-box">❌ {result["message"]}</div>',
                    unsafe_allow_html=True
                )


def show_build_kb_page():
    """Build knowledge base page"""
    st.markdown("### 🧠 Build Knowledge Base")

    st.markdown("""
    Process uploaded documents and build the AI knowledge base. This creates vector embeddings
    of your documentation for efficient retrieval during test case generation.
    """)

    # Options
    col1, col2 = st.columns(2)

    with col1:
        clear_existing = st.checkbox(
            "Clear existing knowledge base",
            value=True,
            help="Clear all existing documents before adding new ones"
        )

    with col2:
        st.info(f"📍 Using AWS Bedrock in {os.getenv('AWS_REGION', 'us-east-1')}")

    # Upload HTML file
    st.markdown("#### Upload checkout.html (Target Web Project)")

    html_file = st.file_uploader(
        "Upload the HTML file to test",
        type=['html'],
        key="html_uploader"
    )

    if html_file:
        html_content = html_file.getvalue().decode('utf-8')
        st.session_state['html_content'] = html_content
        st.success(f"✅ Loaded {html_file.name} ({len(html_content)} characters)")

        with st.expander("Preview HTML"):
            st.code(html_content[:1000] + "..." if len(html_content) > 1000 else html_content, language='html')

    # Build button
    if st.button("Build Knowledge Base", type="primary"):
        if 'uploaded_file_paths' not in st.session_state:
            st.warning("⚠️ Please upload documents first!")
        else:
            with st.spinner("Building knowledge base... This may take a few minutes."):
                file_paths = st.session_state.get('uploaded_file_paths', [])

                # Add HTML file if uploaded
                if html_file:
                    html_path = Path("./uploaded_files") / html_file.name
                    html_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    file_paths.append(str(html_path))

                result = build_knowledge_base(file_paths, clear_existing)

            if result.get('success'):
                st.markdown(
                    f'<div class="success-box">✅ {result["message"]}</div>',
                    unsafe_allow_html=True
                )

                # Display stats
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Files Processed", result.get('files_processed', 0))
                with col2:
                    st.metric("Chunks Created", result.get('chunks_created', 0))
                with col3:
                    st.metric("Documents Added", result.get('documents_added', 0))
                with col4:
                    st.metric("Total Documents", result.get('num_documents', 0))

                st.balloons()

            else:
                st.markdown(
                    f'<div class="error-box">❌ {result["message"]}</div>',
                    unsafe_allow_html=True
                )


def show_generate_test_cases_page():
    """Generate test cases page"""
    st.markdown("### ✍️ Generate Test Cases")

    st.markdown("""
    Generate comprehensive test cases based on your documentation. The AI will create test cases
    grounded strictly in the provided documents.
    """)

    # Input section
    col1, col2 = st.columns([3, 1])

    with col1:
        query = st.text_area(
            "What test cases do you want to generate?",
            placeholder="Example: Generate test cases for discount code functionality",
            height=100
        )

    with col2:
        top_k = st.slider("Relevant docs", 1, 10, 5)

    # Options
    col1, col2, col3 = st.columns(3)

    with col1:
        include_positive = st.checkbox("Positive scenarios", value=True)
    with col2:
        include_negative = st.checkbox("Negative scenarios", value=True)
    with col3:
        include_edge_cases = st.checkbox("Edge cases", value=True)

    # Generate buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate Test Cases", type="primary", disabled=not query):
            with st.spinner("Generating test cases... This may take a minute."):
                result = generate_test_cases(
                    query=query,
                    top_k=top_k,
                    include_positive=include_positive,
                    include_negative=include_negative,
                    include_edge_cases=include_edge_cases
                )

            if result.get('success'):
                st.session_state['test_cases'] = result.get('test_cases', [])
                st.session_state['test_case_sources'] = result.get('sources', [])
                st.session_state['generation_time'] = result.get('generation_time', 0)

            else:
                st.error(result.get('message', 'Error generating test cases'))

    with col2:
        if st.button("Generate All Test Cases"):
            with st.spinner("Generating comprehensive test cases... This may take several minutes."):
                result = generate_all_test_cases()

            if result.get('success'):
                st.session_state['test_cases'] = result.get('test_cases', [])

            else:
                st.error(result.get('message', 'Error generating test cases'))

    # Display results
    if 'test_cases' in st.session_state and st.session_state['test_cases']:
        test_cases = st.session_state['test_cases']

        st.markdown("---")
        st.markdown(f"### 📋 Generated Test Cases ({len(test_cases)})")

        if 'generation_time' in st.session_state:
            st.info(f"⏱️ Generated in {st.session_state['generation_time']:.2f} seconds")

        if 'test_case_sources' in st.session_state:
            st.markdown("**Source Documents:**")
            for source in st.session_state['test_case_sources']:
                st.markdown(f"- {source}")

        # Display test cases
        for idx, test_case in enumerate(test_cases):
            display_test_case(test_case, idx)

        # Download button
        st.download_button(
            label="Download Test Cases (JSON)",
            data=json.dumps(test_cases, indent=2),
            file_name="test_cases.json",
            mime="application/json"
        )


def show_selenium_generator_page():
    """Selenium script generator page"""
    st.markdown("### 🔧 Generate Selenium Scripts")

    st.markdown("""
    Convert test cases into executable Selenium Python scripts.
    """)

    # Check if we have test cases
    if 'test_cases' not in st.session_state or not st.session_state['test_cases']:
        st.warning("⚠️ No test cases available. Please generate test cases first!")
        return

    test_cases = st.session_state['test_cases']

    # Test case selector
    test_case_options = [
        f"{tc.get('test_id', f'TC-{i}')} - {tc.get('feature', 'Unknown')}: {tc.get('test_scenario', 'Unknown')}"
        for i, tc in enumerate(test_cases)
    ]

    selected_option = st.selectbox("Select a test case:", test_case_options)

    selected_index = test_case_options.index(selected_option)
    selected_test_case = test_cases[selected_index]

    # Display selected test case
    st.markdown("#### Selected Test Case")
    display_test_case(selected_test_case, selected_index)

    # Options
    col1, col2 = st.columns(2)

    with col1:
        include_html = st.checkbox(
            "Include HTML context",
            value=True,
            help="Include the checkout.html content for better selector generation"
        )

    with col2:
        save_to_file = st.checkbox(
            "Save to file",
            value=False,
            help="Save the generated script to a file"
        )

    # Generate button
    if st.button("Generate Selenium Script", type="primary"):
        html_content = st.session_state.get('html_content') if include_html else None

        with st.spinner("Generating Selenium script..."):
            result = generate_selenium_script(
                test_case=selected_test_case,
                html_content=html_content,
                save_to_file=save_to_file
            )

        if result.get('success'):
            st.markdown(
                f'<div class="success-box">✅ {result["message"]}</div>',
                unsafe_allow_html=True
            )

            script = result.get('script')

            if script:
                st.markdown("#### Generated Selenium Script")

                # Display script
                st.code(script, language='python')

                # Download button
                st.download_button(
                    label="Download Script",
                    data=script,
                    file_name=f"test_{selected_test_case.get('test_id', 'unknown').lower()}.py",
                    mime="text/x-python"
                )

                if result.get('file_path'):
                    st.info(f"💾 Script saved to: {result['file_path']}")

                if result.get('generation_time'):
                    st.info(f"⏱️ Generated in {result['generation_time']:.2f} seconds")

        else:
            st.markdown(
                f'<div class="error-box">❌ {result["message"]}</div>',
                unsafe_allow_html=True
            )


def show_statistics_page():
    """Statistics page"""
    st.markdown("### 📈 Statistics & Information")

    try:
        # Knowledge base stats
        stats_result = get_kb_stats()

        if stats_result.get('success'):
            stats = stats_result.get('stats', {})

            st.markdown("#### Knowledge Base")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Documents", stats.get('num_documents', 0))
            with col2:
                st.metric("Index Size", stats.get('index_size', 0))
            with col3:
                st.metric("Embedding Dim", stats.get('embedding_dimension', 0))

            st.markdown(f"**Collection:** {stats.get('collection_name', 'N/A')}")
            st.markdown(f"**Store Path:** {stats.get('store_path', 'N/A')}")

        # API health
        st.markdown("---")
        st.markdown("#### API Health")

        response = requests.get(f"{API_BASE_URL}/health")
        health = response.json()

        st.json(health)

    except Exception as e:
        st.error(f"Error fetching statistics: {str(e)}")


if __name__ == "__main__":
    main()
