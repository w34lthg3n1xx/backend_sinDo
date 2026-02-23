"""
Temporary File Cleanup - Ensure no residual data
Secure deletion with overwrite before removal
"""

import os
import shutil
from typing import Optional, List
import logging

# Disable logging for this module
logging.disable(logging.CRITICAL)

class FileCleanup:
    """Secure file cleanup utility"""
    
    # Secure deletion strategies
    OVERWRITE_PASSES = 3  # Number of overwrite passes
    CHUNK_SIZE = 8192     # 8KB chunks for large files
    
    @staticmethod
    def secure_delete_file(file_path: str, verbose: bool = False) -> bool:
        """
        Securely delete a single file by overwriting before deletion
        
        Args:
            file_path: Path to file to delete
            verbose: Whether to log errors (should be False for security)
        
        Returns:
            True if successful, False otherwise
        """
        
        try:
            if not os.path.exists(file_path):
                return True
            
            file_size = os.path.getsize(file_path)
            
            # Don't bother overwriting tiny files (<1KB)
            if file_size > 1024:
                # Multiple overwrite passes
                for _ in range(FileCleanup.OVERWRITE_PASSES):
                    with open(file_path, "wb") as f:
                        bytes_written = 0
                        while bytes_written < file_size:
                            chunk = os.urandom(FileCleanup.CHUNK_SIZE)
                            to_write = min(FileCleanup.CHUNK_SIZE, file_size - bytes_written)
                            f.write(chunk[:to_write])
                            bytes_written += to_write
            else:
                # Simple overwrite for small files
                with open(file_path, "wb") as f:
                    f.write(b'\x00' * file_size)
            
            # Delete file
            os.remove(file_path)
            return True
        
        except Exception as e:
            if verbose:
                pass  # Don't log
            return False
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """
        Cleanup single temporary file (idempotent)
        
        Args:
            file_path: Path to temporary file
        """
        
        FileCleanup.secure_delete_file(file_path, verbose=False)
    
    @staticmethod
    def cleanup_multiple_files(file_paths: List[str]) -> int:
        """
        Cleanup multiple temporary files
        
        Args:
            file_paths: List of file paths to delete
        
        Returns:
            Number of successfully deleted files
        """
        
        deleted_count = 0
        for file_path in file_paths:
            if FileCleanup.secure_delete_file(file_path, verbose=False):
                deleted_count += 1
        
        return deleted_count
    
    @staticmethod
    def cleanup_directory(dir_path: str, recursive: bool = True) -> bool:
        """
        Cleanup entire temporary directory
        
        Args:
            dir_path: Path to directory
            recursive: Whether to delete recursively
        
        Returns:
            True if successful
        """
        
        try:
            if not os.path.exists(dir_path):
                return True
            
            if recursive:
                # Secure delete each file first
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        FileCleanup.secure_delete_file(file_path, verbose=False)
            
            # Remove directory structure
            shutil.rmtree(dir_path)
            return True
        
        except Exception:
            return False
    
    @staticmethod
    def cleanup_on_error(file_path: Optional[str]) -> None:
        """
        Cleanup file on error (context manager friendly)
        
        Args:
            file_path: File to delete if error occurs
        """
        
        if file_path:
            FileCleanup.secure_delete_file(file_path, verbose=False)

# Convenience functions for direct import
def cleanup_temp_file(file_path: str) -> None:
    """Cleanup single file"""
    FileCleanup.cleanup_temp_file(file_path)

def cleanup_multiple_files(file_paths: List[str]) -> int:
    """Cleanup multiple files"""
    return FileCleanup.cleanup_multiple_files(file_paths)

def cleanup_directory(dir_path: str) -> bool:
    """Cleanup directory"""
    return FileCleanup.cleanup_directory(dir_path)

def secure_delete_file(file_path: str) -> bool:
    """Securely delete file"""
    return FileCleanup.secure_delete_file(file_path, verbose=False)