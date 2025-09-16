#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify all imports work correctly
"""

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        # Test main module
        from main import QualityControlPipeline
        print("[OK] main module imported successfully")
        
        # Test validators
        from modules.validators.fastq_validator import FastqValidator
        from modules.validators.bam_validator import BamValidator
        from modules.validators.vcf_validator import VcfValidator
        print("[OK] All validators imported successfully")
        
        # Test QC engines
        from modules.qc_engines.base_qc import BaseQCEngine
        from modules.qc_engines.fastq_qc import FastqQCEngine
        from modules.qc_engines.bam_qc import BamQCEngine
        from modules.qc_engines.vcf_qc import VcfQCEngine
        print("[OK] All QC engines imported successfully")
        
        # Test reporters
        from modules.reporters.base_reporter import BaseReporter
        from modules.reporters.json_reporter import JSONReporter
        from modules.reporters.html_reporter import HTMLReporter
        from modules.reporters.text_reporter import TextReporter
        print("[OK] All reporters imported successfully")
        
        # Test pipeline creation
        pipeline = QualityControlPipeline()
        print("[OK] QualityControlPipeline created successfully")
        
        print("\n[SUCCESS] All imports and basic functionality work correctly!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during import test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()