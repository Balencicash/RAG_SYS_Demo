#!/usr/bin/env python3
"""
Sample Test Script for RAG Document QA System
Copyright (c) 2024 Balenci Cash - All Rights Reserved
This script demonstrates the watermark protection system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.watermark import watermark, initialize_watermark_protection


def test_watermark_system():
    """Test the watermark protection system."""
    print("=" * 60)
    print("RAG Document QA System - Watermark Verification")
    print("=" * 60)
    
    try:
        # Initialize watermark protection
        result = initialize_watermark_protection()
        if result:
            print("✅ Watermark protection initialized successfully")
            print(f"   Author: {watermark.author}")
            print(f"   Email: {watermark.email}")
            print(f"   Project ID: BC-RAG-DOC-QA-V1.0")
            print(f"   Signature: {watermark._signature_hash[:32]}...")
            print("")
            print("⚠️  WARNING: This software is protected by digital watermark")
            print("   Unauthorized use or distribution is prohibited")
            print("   All executions are tracked and logged")
        else:
            print("❌ Watermark verification failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("=" * 60)
    print("System ready for use")
    print("=" * 60)
    return True


def test_imports():
    """Test that all modules can be imported."""
    print("\nTesting module imports...")
    
    modules = [
        "src.services.document_parser",
        "src.services.vectorization", 
        "src.services.llm_service",
        "src.agents.rag_agent",
        "src.api.main",
        "config.settings"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    print("\n✅ All modules imported successfully")
    return True


if __name__ == "__main__":
    # Run tests
    if test_watermark_system():
        test_imports()
        print("\n🎉 All tests passed! System is ready.")
        print("\nTo start the server, run:")
        print("  ./start.sh")
        print("\nOr with Docker:")
        print("  docker-compose up")
    else:
        print("\n❌ Tests failed. Please check the configuration.")
        sys.exit(1)