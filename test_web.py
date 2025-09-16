#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify web interface works correctly
"""

def test_web_imports():
    """Test that web interface can be imported without errors."""
    try:
        # Test web interface import
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from web_interface import QualityControlPipeline
        print("[OK] web_interface imported QualityControlPipeline successfully")
        
        # Test pipeline creation
        pipeline = QualityControlPipeline()
        print("[OK] QualityControlPipeline created successfully in web context")
        
        print("\n[SUCCESS] Web interface imports work correctly!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during web interface test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_web_imports()