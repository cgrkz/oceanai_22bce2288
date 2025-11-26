#!/usr/bin/env python3
"""Test AWS Bedrock connection"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing AWS Bedrock Connection...")
print("=" * 70)
print(f"AWS Region: {os.getenv('AWS_REGION')}")
print(f"LLM Model: {os.getenv('BEDROCK_LLM_MODEL_ID')}")
print(f"Embedding Model: {os.getenv('BEDROCK_EMBEDDING_MODEL_ID')}")
print("=" * 70)

try:
    from backend.app.services.bedrock_client import get_bedrock_client

    print("\n✅ Creating Bedrock client...")
    bedrock = get_bedrock_client()

    print("✅ Testing LLM connection (Nova Lite)...")
    response = bedrock.invoke_llm(
        prompt="Say 'Hello QA Agent' in exactly 3 words.",
        max_tokens=20,
        temperature=0.1
    )

    print(f"\n📝 LLM Response:")
    print(f"   '{response.strip()}'")

    print("\n" + "=" * 70)
    print("🎉 AWS BEDROCK CONNECTION SUCCESSFUL!")
    print("=" * 70)
    print("\n✅ Nova Lite LLM is accessible and working!")
    print("✅ Ready to generate test cases and Selenium scripts!")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Start the application: ./start.sh")
    print("2. Open UI: http://localhost:8501")
    print("3. Upload documents and build knowledge base")
    print("4. Generate test cases!")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\n" + "=" * 70)
    print("TROUBLESHOOTING:")
    print("=" * 70)
    print("1. Check AWS credentials in .env file")
    print("2. Verify Bedrock model access in AWS Console:")
    print("   a. Go to: https://console.aws.amazon.com/bedrock/")
    print("   b. Click 'Model Access' in left sidebar")
    print("   c. Click 'Manage model access' button")
    print("   d. Enable: Amazon Nova Lite (amazon.nova-lite-v1:0)")
    print("   e. Enable: Cohere Embed v4 (cohere.embed-v4:0)")
    print("   f. Wait for 'Access granted' status")
    print("\n3. Check IAM permissions include 'bedrock:InvokeModel'")
    print("=" * 70)
    sys.exit(1)
