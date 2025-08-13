"""
File utilities for atomic operations and corruption-safe writes.
Addresses crash mid-write corruption risk identified in ChatGPT-5 review.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List


def atomic_write_jsonl(data: List[Dict], file_path: str) -> bool:
    """
    Atomically write JSONL data to file using temp file + rename.
    
    Prevents corruption from crashes mid-write by writing to temp file first,
    then atomically renaming to target file.
    
    Args:
        data: List of dictionaries to write as JSONL
        file_path: Target file path
        
    Returns:
        True if successful, False if error
    """
    try:
        file_path = Path(file_path)
        
        # Create temp file in same directory as target
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.tmp',
            prefix=file_path.name + '_',
            dir=file_path.parent
        )
        
        try:
            # Write data to temp file
            with os.fdopen(temp_fd, 'w') as f:
                for record in data:
                    f.write(json.dumps(record) + '\n')
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            # Atomically replace target file
            os.replace(temp_path, file_path)
            return True
            
        except Exception:
            # Clean up temp file if write failed
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise
            
    except Exception as e:
        print(f"❌ Atomic write failed for {file_path}: {e}")
        return False


def atomic_append_jsonl(records: List[Dict], file_path: str) -> bool:
    """
    Atomically append JSONL records to file.
    
    Reads existing file, appends new records, then atomically writes back.
    
    Args:
        records: List of records to append
        file_path: Target file path
        
    Returns:
        True if successful, False if error
    """
    try:
        existing_records = []
        
        # Read existing records if file exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            existing_records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        
        # Combine existing + new records
        all_records = existing_records + records
        
        # Atomically write combined data
        return atomic_write_jsonl(all_records, file_path)
        
    except Exception as e:
        print(f"❌ Atomic append failed for {file_path}: {e}")
        return False


def safe_backup_file(file_path: str, backup_suffix: str = '.backup') -> str:
    """
    Create a backup copy of file before modification.
    
    Args:
        file_path: Path to file to backup
        backup_suffix: Suffix for backup file
        
    Returns:
        Path to backup file, or empty string if failed
    """
    try:
        if not os.path.exists(file_path):
            return ""
        
        backup_path = file_path + backup_suffix
        
        # Copy with metadata preservation
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return backup_path
        
    except Exception as e:
        print(f"❌ Backup failed for {file_path}: {e}")
        return ""


def atomic_jsonl_update(file_path: str, update_func: callable) -> bool:
    """
    Atomically update JSONL file using update function.
    
    Reads file, applies update function, writes back atomically.
    
    Args:
        file_path: Path to JSONL file
        update_func: Function that takes List[Dict] and returns List[Dict]
        
    Returns:
        True if successful, False if error
    """
    try:
        # Read existing records
        records = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        
        # Apply update function
        updated_records = update_func(records)
        
        # Atomically write updated data
        return atomic_write_jsonl(updated_records, file_path)
        
    except Exception as e:
        print(f"❌ Atomic update failed for {file_path}: {e}")
        return False


if __name__ == '__main__':
    # Test atomic write operations
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, 'test_atomic.jsonl')
        
        # Test atomic write
        test_data = [
            {'date': '2025-08-01', 'score': 65},
            {'date': '2025-08-02', 'score': 70}
        ]
        
        success = atomic_write_jsonl(test_data, test_file)
        print(f"✅ Atomic write: {success}")
        
        # Test atomic append
        new_data = [{'date': '2025-08-03', 'score': 75}]
        success = atomic_append_jsonl(new_data, test_file)
        print(f"✅ Atomic append: {success}")
        
        # Verify final content
        with open(test_file, 'r') as f:
            lines = f.readlines()
            print(f"✅ Final file has {len(lines)} records")
            
        # Test update function
        def increment_scores(records):
            for record in records:
                record['score'] += 5
            return records
            
        success = atomic_jsonl_update(test_file, increment_scores)
        print(f"✅ Atomic update: {success}")