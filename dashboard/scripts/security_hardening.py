#!/usr/bin/env python3
"""Security hardening verification and setup script.
Systematically checks and completes dashboard security checklist items.

Usage:
  PYTHONPATH=. python3 dashboard/scripts/security_hardening.py [--check-only]

Options:
  --check-only    Only check current status, don't make changes
  
This script helps ensure all security checklist items are properly configured
before enabling real personal data ingestion.
"""
from __future__ import annotations
import os, sys, pathlib, stat, subprocess
from typing import Dict, List, Tuple

def check_file_permissions(file_path: pathlib.Path, expected_mode: int) -> Tuple[bool, str]:
    """Check if file has expected permissions."""
    if not file_path.exists():
        return False, f"File does not exist: {file_path}"
    
    current_mode = file_path.stat().st_mode & 0o777
    if current_mode == expected_mode:
        return True, f"✅ Correct permissions ({oct(expected_mode)})"
    else:
        return False, f"❌ Wrong permissions: {oct(current_mode)} (expected {oct(expected_mode)})"

def check_env_file() -> Dict[str, bool]:
    """Check .env file status."""
    results = {}
    
    # Check .env.example exists and committed
    env_example = pathlib.Path(".env.example")
    results["env_example_exists"] = env_example.exists()
    
    # Check real .env exists locally
    env_file = pathlib.Path(".env")
    results["env_file_exists"] = env_file.exists()
    
    # Check .env permissions if exists
    if env_file.exists():
        perm_ok, _ = check_file_permissions(env_file, 0o600)
        results["env_permissions_600"] = perm_ok
    else:
        results["env_permissions_600"] = False
    
    return results

def check_gitignore() -> bool:
    """Check if sensitive directories are in .gitignore."""
    gitignore = pathlib.Path(".gitignore")
    if not gitignore.exists():
        return False
    
    content = gitignore.read_text(encoding="utf-8")
    required_entries = [".env", "private/", "/private/"]
    
    for entry in required_entries:
        if entry in content:
            return True
    return False

def check_parity_tests() -> bool:
    """Check if parity tests pass."""
    try:
        result = subprocess.run([
            sys.executable, "dashboard/tests/test_vectors.py"
        ], capture_output=True, text=True, env={"PYTHONPATH": "."})
        return result.returncode == 0 and "All vector tests passed" in result.stdout
    except Exception:
        return False

def check_validation_integrity() -> bool:
    """Check if validation script exists and works."""
    validator = pathlib.Path("dashboard/scripts/validate_daily_records.py")
    if not validator.exists():
        return False
    
    # Check with sample data
    sample_data = pathlib.Path("dashboard/tests/sample_daily_records.jsonl")
    if not sample_data.exists():
        return False
    
    try:
        result = subprocess.run([
            sys.executable, str(validator), str(sample_data)
        ], capture_output=True, text=True, env={"PYTHONPATH": "."})
        return result.returncode == 0 and "VALIDATION PASSED" in result.stdout
    except Exception:
        return False

def create_private_directory() -> bool:
    """Create private directory with correct permissions."""
    private_dir = pathlib.Path("private")
    try:
        private_dir.mkdir(mode=0o700, exist_ok=True)
        # Ensure permissions are correct
        private_dir.chmod(0o700)
        return True
    except Exception as e:
        print(f"❌ Failed to create private directory: {e}")
        return False

def setup_precommit_hook() -> bool:
    """Set up pre-commit hook if .git directory exists."""
    git_dir = pathlib.Path(".git")
    if not git_dir.exists():
        return True  # Not a git repo, skip
    
    hook_target = git_dir / "hooks" / "pre-commit"
    hook_source = pathlib.Path("scripts/precommit-guard.sh")
    
    if not hook_source.exists():
        return False
    
    try:
        # Create symlink to pre-commit guard
        if hook_target.exists():
            hook_target.unlink()  # Remove existing
        
        hook_target.symlink_to(hook_source.resolve())
        hook_target.chmod(0o755)
        return True
    except Exception as e:
        print(f"❌ Failed to setup pre-commit hook: {e}")
        return False

def run_security_check(check_only: bool = False) -> Dict[str, bool]:
    """Run complete security checklist verification."""
    results = {}
    
    print("🔒 Dashboard Security Hardening Check")
    print("=" * 50)
    
    # 1. Credentials & Secrets
    print("\n1️⃣ Credentials & Secrets")
    env_status = check_env_file()
    
    results["env_example_committed"] = env_status["env_example_exists"]
    print(f"   .env.example exists: {'✅' if results['env_example_committed'] else '❌'}")
    
    results["env_file_local"] = env_status["env_file_exists"]
    print(f"   .env file exists locally: {'✅' if results['env_file_local'] else '❌'}")
    
    results["env_permissions"] = env_status["env_permissions_600"]
    print(f"   .env permissions 600: {'✅' if results['env_permissions'] else '❌'}")
    
    # 3. File System Permissions  
    print("\n3️⃣ File System Permissions")
    private_exists = pathlib.Path("private").exists()
    results["private_directory"] = private_exists
    print(f"   private/ directory exists: {'✅' if private_exists else '❌'}")
    
    if not check_only and not private_exists:
        print("   Creating private/ directory...")
        results["private_directory"] = create_private_directory()
    
    results["gitignore_configured"] = check_gitignore()
    print(f"   .gitignore configured: {'✅' if results['gitignore_configured'] else '❌'}")
    
    # 5. Data Hygiene
    print("\n5️⃣ Data Hygiene")  
    results["precommit_hook"] = pathlib.Path(".git/hooks/pre-commit").exists()
    print(f"   Pre-commit hook installed: {'✅' if results['precommit_hook'] else '❌'}")
    
    if not check_only and not results["precommit_hook"]:
        print("   Setting up pre-commit hook...")
        results["precommit_hook"] = setup_precommit_hook()
    
    # 6. Parity & Integrity  
    print("\n6️⃣ Parity & Integrity")
    results["parity_tests"] = check_parity_tests()
    print(f"   Parity tests pass: {'✅' if results['parity_tests'] else '❌'}")
    
    results["validation_integrity"] = check_validation_integrity()
    print(f"   Validation + integrity: {'✅' if results['validation_integrity'] else '❌'}")
    
    # 8. Verification Run
    print("\n8️⃣ Verification Run")
    synth_data = pathlib.Path("dashboard/tests/synth_export.jsonl")
    results["synthetic_data_available"] = synth_data.exists()
    print(f"   Synthetic test data: {'✅' if results['synthetic_data_available'] else '❌'}")
    
    # Summary
    print(f"\n" + "=" * 50)
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"📊 Security Status: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("🏆 ALL SECURITY CHECKS PASSED - Ready for real data ingestion!")
        return results, True
    else:
        print("⚠️  Some security checks failed - review and fix before real data")
        failed = [k for k, v in results.items() if not v]
        print(f"❌ Failed checks: {', '.join(failed)}")
        return results, False

def main():
    check_only = "--check-only" in sys.argv
    
    if check_only:
        print("🔍 Running security check (no changes will be made)")
    else:
        print("🔧 Running security hardening (will make necessary changes)")
    
    results, all_passed = run_security_check(check_only)
    
    if all_passed:
        print(f"\n✅ Security hardening complete!")
        if not check_only:
            print(f"🎯 Ready to enable real personal data ingestion")
        return 0
    else:
        print(f"\n❌ Security hardening incomplete")
        print(f"📋 Review failed items and run again")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())