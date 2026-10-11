"""
Security / Secret Scanner

Scans the complete project for:
- Passwords
- API keys
- JWT tokens
- Cookies
- Authorization headers
- Session files
- Authentication tokens
- Embedded credentials

Never prints actual secret values.
Returns PASS or FAIL with filename and secret category.
"""
import re
import json
from pathlib import Path
from typing import List, Tuple, Optional


class SecretScanner:
    """
    Scans project files for secrets and sensitive data.
    """
    
    # Patterns for detecting secrets (regex patterns)
    SECRET_PATTERNS = {
        "api_key": [
            r'api[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}["\']?',
            r'apikey\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}["\']?',
            r'GEMINI_API_KEY\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?',
            r'GROQ_API_KEY\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?',
        ],
        "password": [
            r'password\s*[:=]\s*["\']?[^"\s]{8,}["\']?',
            r'passwd\s*[:=]\s*["\']?[^"\s]{8,}["\']?',
            r'secret\s*[:=]\s*["\']?[^"\s]{8,}["\']?',
        ],
        "jwt_token": [
            r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
        ],
        "authorization_header": [
            r'authorization\s*[:=]\s*["\']?(bearer|basic)\s+[a-zA-Z0-9_-]{10,}["\']?',
            r'auth\s*[:=]\s*["\']?(bearer|basic)\s+[a-zA-Z0-9_-]{10,}["\']?',
        ],
        "session_token": [
            r'session[_-]?id\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}["\']?',
            r'token\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}["\']?',
        ],
        "cookie": [
            r'cookie\s*[:=]\s*["\']?[a-zA-Z0-9%_-]{20,}["\']?',
        ],
    }
    
    # File patterns to exclude from scanning
    EXCLUDE_PATTERNS = [
        "*.pyc",
        "*.pyo",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "*.egg-info",
        "*.dist-info",
        "node_modules",
    ]
    
    # File patterns that are expected to contain secrets (should be gitignored)
    EXPECTED_SECRET_FILES = [
        ".env",
        "session_*.json",
        "learned_answers.json",
    ]
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.findings: List[Tuple[str, str, str]] = []  # (file, category, line_number)
    
    def should_scan_file(self, file_path: Path) -> bool:
        """Check if a file should be scanned."""
        # Check exclude patterns
        for pattern in self.EXCLUDE_PATTERNS:
            if file_path.match(pattern):
                return False
        
        # Check if it's in an excluded directory
        for part in file_path.parts:
            if part in [".git", ".venv", "venv", "__pycache__", "node_modules"]:
                return False
        
        return True
    
    def is_expected_secret_file(self, file_path: Path) -> bool:
        """Check if a file is expected to contain secrets (should be gitignored)."""
        filename = file_path.name
        for pattern in self.EXPECTED_SECRET_FILES:
            if file_path.match(pattern):
                return True
        return False
    
    def scan_file(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """
        Scan a single file for secrets.
        
        Returns list of (category, line_content, line_number) tuples.
        Never prints actual secret values.
        """
        findings = []
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return findings
        
        for line_number, line in enumerate(lines, 1):
            for category, patterns in self.SECRET_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Mask the secret value in the output
                        masked_line = self._mask_secret(line)
                        findings.append((category, masked_line, line_number))
                        break  # Only report each line once
        
        return findings
    
    def _mask_secret(self, line: str) -> str:
        """Mask secret values in a line for safe display."""
        # Replace long alphanumeric sequences with ***
        masked = re.sub(r'[a-zA-Z0-9_-]{20,}', '***', line)
        return masked.strip()
    
    def scan_project(self) -> bool:
        """
        Scan the entire project for secrets.
        
        Returns True if scan passed (no unexpected secrets), False otherwise.
        """
        print(f"Scanning project: {self.project_root}")
        print("="*60)
        
        all_findings = []
        
        # Scan all files
        for file_path in self.project_root.rglob("*"):
            if not file_path.is_file():
                continue
            
            if not self.should_scan_file(file_path):
                continue
            
            findings = self.scan_file(file_path)
            if findings:
                for category, masked_line, line_number in findings:
                    relative_path = file_path.relative_to(self.project_root)
                    is_expected = self.is_expected_secret_file(file_path)
                    
                    status = "EXPECTED" if is_expected else "UNEXPECTED"
                    all_findings.append((str(relative_path), category, line_number, status, masked_line))
        
        # Report findings
        if not all_findings:
            print("OK: No secrets found in source code")
            print("="*60)
            return True
        
        # Separate expected from unexpected
        expected = [f for f in all_findings if f[3] == "EXPECTED"]
        unexpected = [f for f in all_findings if f[3] == "UNEXPECTED"]
        
        if expected:
            print("\nExpected secret files (should be gitignored):")
            for file_path, category, line_number, status, masked_line in expected:
                print(f"  {file_path}:{line_number} - {category}")
                print(f"    {masked_line[:80]}...")
        
        if unexpected:
            print("\nWARNING: UNEXPECTED SECRETS FOUND:")
            for file_path, category, line_number, status, masked_line in unexpected:
                print(f"  {file_path}:{line_number} - {category}")
                print(f"    {masked_line[:80]}...")
        
        print("="*60)
        
        if unexpected:
            print("SCAN RESULT: FAIL")
            print("Please remove or secure the unexpected secrets above.")
            return False
        else:
            print("SCAN RESULT: PASS")
            print("All secrets are in expected gitignored files.")
            return True
    
    def check_gitignore(self) -> bool:
        """
        Check if secret files are properly gitignored.
        
        Returns True if all expected secret files are gitignored, False otherwise.
        """
        gitignore_path = self.project_root / ".gitignore"
        
        if not gitignore_path.exists():
            print("WARNING: No .gitignore file found")
            return False
        
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gitignore_content = f.read()
        
        missing = []
        for pattern in self.EXPECTED_SECRET_FILES:
            # Convert glob pattern to simple check
            if pattern not in gitignore_content:
                missing.append(pattern)
        
        if missing:
            print("WARNING: The following patterns are missing from .gitignore:")
            for pattern in missing:
                print(f"  {pattern}")
            return False
        
        print("OK: All expected secret patterns are in .gitignore")
        return True


def main():
    """Run the security scanner."""
    import sys
    
    # Determine project root
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = Path(__file__).parent
    
    scanner = SecretScanner(project_root)
    
    print("\n" + "="*60)
    print("SECURITY / SECRET SCANNER")
    print("="*60)
    
    # Check gitignore
    scanner.check_gitignore()
    print()
    
    # Scan for secrets
    scan_passed = scanner.scan_project()
    
    if not scan_passed:
        sys.exit(1)
    
    print("\nOK: Security check passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
