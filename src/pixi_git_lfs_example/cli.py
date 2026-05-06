"""
CLI utility to check if a file is a Git LFS pointer or actual binary content.

This utility helps diagnose issues with Pixi installing packages that use Git LFS
for storing binary files. If Pixi fails to properly handle Git LFS, the installed
files will be Git LFS pointers instead of actual binary files.
"""

import argparse
from importlib import resources
import sys
from pathlib import Path


def default_stl_path() -> Path:
    """Return the packaged binary_cube.stl path."""
    return Path(resources.files("pixi_git_lfs_example.data").joinpath("binary_cube.stl"))


def is_git_lfs_pointer(file_path: Path) -> bool:
    """
    Check if a file is a Git LFS pointer file.
    
    Git LFS pointer files are text files that start with "version https://git-lfs.github.com/spec/v1"
    and contain metadata about the actual file stored in Git LFS.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file is a Git LFS pointer, False otherwise
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            return first_line.startswith("version https://git-lfs.github.com/spec/v1")
    except (UnicodeDecodeError, IOError):
        # If we can't read as text, it's likely a binary file
        return False


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Check if a file is a Git LFS pointer or actual binary content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
This tool helps diagnose Pixi Git LFS installation issues. 

Examples:
    check-stl-is-not-git-lfs-pointer
    check-stl-is-not-git-lfs-pointer /path/to/another-file.stl
  
Exit codes:
  0: File is a proper binary/binary file (not a Git LFS pointer)
  1: File is a Git LFS pointer (indicates installation problem)
  2: File not found or other error
"""
    )
    
    parser.add_argument(
                "file",
                nargs="?",
                default=None,
                help="Path to the file to check (defaults to packaged data/binary_cube.stl)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed information"
    )
    
    args = parser.parse_args()
    
    try:
        file_path = Path(args.file) if args.file is not None else default_stl_path()
        
        if is_git_lfs_pointer(file_path):
            if args.verbose:
                print(f"❌ ERROR: {file_path} is a Git LFS pointer file, not the actual binary content")
                print("   This indicates that Pixi failed to properly download and install the Git LFS content")
                with open(file_path, 'r') as f:
                    print("   Content:")
                    for line in f:
                        print(f"     {line.rstrip()}")
            else:
                print(f"ERROR: {file_path} is a Git LFS pointer (not actual binary content)")
            return 1
        else:
            if args.verbose:
                size = file_path.stat().st_size
                print(f"✓ OK: {file_path} is proper binary content (size: {size} bytes)")
            else:
                print(f"OK: {file_path} is proper binary content")
            return 0
            
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
