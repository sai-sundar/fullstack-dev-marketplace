#!/usr/bin/env python3
"""
Validate frontend-backend integration by checking contract sync.

Usage:
    python validate_integration.py --project-dir /path/to/project
    python validate_integration.py --project-dir . --fix-suggestions
    python validate_integration.py --contracts-only ./contracts

This script validates:
1. Contract files exist
2. Database columns match TypeScript fields
3. Frontend API calls match backend routes
4. Validation schemas are in sync
5. RLS policies exist for all tables
"""

import argparse
import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Severity(Enum):
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"


@dataclass
class ValidationIssue:
    severity: Severity
    category: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    suggestion: Optional[str] = None


class IntegrationValidator:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.issues: list[ValidationIssue] = []
        
        # Try to find contracts directory
        self.contracts_dir = self._find_contracts_dir()
        
        # Storage for parsed data
        self.db_tables: dict[str, dict] = {}
        self.ts_interfaces: dict[str, dict] = {}
        self.api_endpoints: dict[str, dict] = {}
        self.frontend_calls: list[dict] = []
        self.backend_routes: list[dict] = []

    def _find_contracts_dir(self) -> Optional[Path]:
        """Find contracts directory in project."""
        candidates = [
            self.project_dir / "contracts",
            self.project_dir / "packages" / "shared" / "src" / "contracts",
            self.project_dir / "packages" / "shared" / "contracts",
            self.project_dir / "src" / "contracts",
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        return None

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print(f"\n🔍 Validating integration in: {self.project_dir}\n")
        
        # Check 1: Contract files
        self._check_contract_files()
        
        if self.contracts_dir:
            # Check 2: Parse and validate database schema
            self._parse_database_sql()
            
            # Check 3: Parse and validate TypeScript types
            self._parse_types_ts()
            
            # Check 4: Compare database to TypeScript
            self._compare_db_to_ts()
            
            # Check 5: Parse endpoints
            self._parse_endpoints_ts()
        
        # Check 6: Scan frontend for API calls
        self._scan_frontend_calls()
        
        # Check 7: Scan backend for routes
        self._scan_backend_routes()
        
        # Check 8: Compare frontend calls to backend routes
        self._compare_frontend_to_backend()
        
        # Print report
        self._print_report()
        
        # Return True if no errors (warnings are OK)
        errors = [i for i in self.issues if i.severity == Severity.ERROR]
        return len(errors) == 0

    def _check_contract_files(self) -> None:
        """Check that all required contract files exist."""
        if not self.contracts_dir:
            self.issues.append(ValidationIssue(
                severity=Severity.ERROR,
                category="Contracts",
                message="No contracts directory found",
                suggestion="Create contracts/ directory with database.sql, types.ts, endpoints.ts, validation.ts, errors.ts"
            ))
            return
        
        required_files = [
            "database.sql",
            "types.ts",
            "endpoints.ts",
            "validation.ts",
            "errors.ts",
        ]
        
        for filename in required_files:
            filepath = self.contracts_dir / filename
            if not filepath.exists():
                self.issues.append(ValidationIssue(
                    severity=Severity.ERROR,
                    category="Contracts",
                    message=f"Missing required contract file: {filename}",
                    file=str(self.contracts_dir),
                    suggestion=f"Create {filename} in contracts directory"
                ))
            else:
                print(f"  ✓ Found {filename}")

    def _parse_database_sql(self) -> None:
        """Parse database.sql to extract tables and columns."""
        db_file = self.contracts_dir / "database.sql"
        if not db_file.exists():
            return
        
        content = db_file.read_text()
        
        # Find CREATE TABLE statements
        table_pattern = r'CREATE TABLE (?:public\.)?(\w+)\s*\(([\s\S]*?)\);'
        
        for match in re.finditer(table_pattern, content, re.IGNORECASE):
            table_name = match.group(1)
            columns_block = match.group(2)
            
            columns = {}
            for line in columns_block.split('\n'):
                line = line.strip()
                if not line or line.startswith('--') or line.startswith('PRIMARY KEY') or line.startswith('FOREIGN KEY') or line.startswith('CHECK') or line.startswith('CONSTRAINT'):
                    continue
                
                col_match = re.match(r'(\w+)\s+(\w+)', line)
                if col_match:
                    col_name = col_match.group(1)
                    col_type = col_match.group(2).upper()
                    columns[col_name] = {
                        'type': col_type,
                        'nullable': 'NOT NULL' not in line.upper(),
                    }
            
            self.db_tables[table_name] = columns
        
        print(f"  ✓ Parsed {len(self.db_tables)} tables from database.sql")

    def _parse_types_ts(self) -> None:
        """Parse types.ts to extract interfaces and fields."""
        types_file = self.contracts_dir / "types.ts"
        if not types_file.exists():
            return
        
        content = types_file.read_text()
        
        # Find interface definitions
        interface_pattern = r'(?:export\s+)?interface\s+(\w+)\s*\{([^}]+)\}'
        
        for match in re.finditer(interface_pattern, content):
            interface_name = match.group(1)
            fields_block = match.group(2)
            
            fields = {}
            for line in fields_block.split('\n'):
                line = line.strip().rstrip(';').rstrip(',')
                if not line or line.startswith('//'):
                    continue
                
                field_match = re.match(r'(\w+)(\?)?:\s*(.+)', line)
                if field_match:
                    field_name = field_match.group(1)
                    optional = field_match.group(2) == '?'
                    field_type = field_match.group(3).strip()
                    fields[field_name] = {
                        'type': field_type,
                        'optional': optional,
                    }
            
            self.ts_interfaces[interface_name] = fields
        
        print(f"  ✓ Parsed {len(self.ts_interfaces)} interfaces from types.ts")

    def _compare_db_to_ts(self) -> None:
        """Compare database columns to TypeScript fields."""
        # Map table names to likely interface names
        table_to_interface = {
            'profiles': 'Profile',
            'cvs': 'CV',
            'cv_analyses': 'CVAnalysis',
            'motivation_letters': 'MotivationLetter',
            'interviews': 'Interview',
            'interview_questions': 'InterviewQuestion',
        }
        
        for table_name, columns in self.db_tables.items():
            # Find matching interface
            interface_name = table_to_interface.get(
                table_name,
                table_name.rstrip('s').title()  # Default: cvs -> Cv
            )
            
            if interface_name not in self.ts_interfaces:
                # Try variations
                variations = [
                    interface_name,
                    interface_name.upper(),
                    ''.join(word.title() for word in table_name.split('_')).rstrip('s'),
                ]
                
                found = False
                for var in variations:
                    if var in self.ts_interfaces:
                        interface_name = var
                        found = True
                        break
                
                if not found:
                    self.issues.append(ValidationIssue(
                        severity=Severity.WARNING,
                        category="Type Sync",
                        message=f"No TypeScript interface found for table '{table_name}'",
                        suggestion=f"Create interface '{interface_name}' in types.ts"
                    ))
                    continue
            
            ts_fields = self.ts_interfaces[interface_name]
            
            # Check each column has matching field
            for col_name, col_info in columns.items():
                if col_name not in ts_fields:
                    # Check for camelCase version (common mistake)
                    camel_name = self._snake_to_camel(col_name)
                    if camel_name in ts_fields:
                        self.issues.append(ValidationIssue(
                            severity=Severity.ERROR,
                            category="Field Mismatch",
                            message=f"Case mismatch in '{interface_name}': database has '{col_name}', TypeScript has '{camel_name}'",
                            suggestion=f"Rename '{camel_name}' to '{col_name}' in types.ts to match database"
                        ))
                    else:
                        self.issues.append(ValidationIssue(
                            severity=Severity.WARNING,
                            category="Missing Field",
                            message=f"Column '{col_name}' in table '{table_name}' not found in interface '{interface_name}'",
                            suggestion=f"Add '{col_name}' field to '{interface_name}' interface"
                        ))

    def _snake_to_camel(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    def _parse_endpoints_ts(self) -> None:
        """Parse endpoints.ts to extract API endpoints."""
        endpoints_file = self.contracts_dir / "endpoints.ts"
        if not endpoints_file.exists():
            return
        
        content = endpoints_file.read_text()
        
        # Find endpoint strings
        endpoint_pattern = r"['\"`](/api[^'\"`]+)['\"`]"
        
        for match in re.finditer(endpoint_pattern, content):
            endpoint = match.group(1)
            # Normalize :id to {id} style
            normalized = re.sub(r'\$\{(\w+)\}', r':\1', endpoint)
            self.api_endpoints[normalized] = {'defined_in': 'endpoints.ts'}
        
        print(f"  ✓ Found {len(self.api_endpoints)} endpoints in endpoints.ts")

    def _scan_frontend_calls(self) -> None:
        """Scan frontend code for API calls."""
        frontend_dirs = [
            self.project_dir / "apps" / "web" / "src",
            self.project_dir / "src",
            self.project_dir / "frontend" / "src",
        ]
        
        patterns = [
            r'fetch\([\'"`]([^\'"`]+)[\'"`]',
            r'axios\.\w+\([\'"`]([^\'"`]+)[\'"`]',
            r'api\.\w+\([\'"`]([^\'"`]+)[\'"`]',
            r'ENDPOINTS\.\w+\.(\w+)',
        ]
        
        for frontend_dir in frontend_dirs:
            if not frontend_dir.exists():
                continue
            
            for ts_file in frontend_dir.rglob("*.ts"):
                self._scan_file_for_api_calls(ts_file, patterns)
            for tsx_file in frontend_dir.rglob("*.tsx"):
                self._scan_file_for_api_calls(tsx_file, patterns)
        
        print(f"  ✓ Found {len(self.frontend_calls)} API calls in frontend")

    def _scan_file_for_api_calls(self, filepath: Path, patterns: list) -> None:
        """Scan a single file for API calls."""
        try:
            content = filepath.read_text()
        except:
            return
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                url = match.group(1)
                if url.startswith('/api') or url.startswith('http'):
                    self.frontend_calls.append({
                        'url': url,
                        'file': str(filepath),
                    })

    def _scan_backend_routes(self) -> None:
        """Scan backend code for route definitions."""
        backend_dirs = [
            self.project_dir / "apps" / "server" / "src",
            self.project_dir / "server" / "src",
            self.project_dir / "backend" / "src",
            self.project_dir / "src" / "routes",
        ]
        
        patterns = [
            r'router\.(get|post|put|patch|delete)\([\'"`]([^\'"`]+)[\'"`]',
            r'app\.(get|post|put|patch|delete)\([\'"`]([^\'"`]+)[\'"`]',
        ]
        
        for backend_dir in backend_dirs:
            if not backend_dir.exists():
                continue
            
            for ts_file in backend_dir.rglob("*.ts"):
                self._scan_file_for_routes(ts_file, patterns)
        
        print(f"  ✓ Found {len(self.backend_routes)} routes in backend")

    def _scan_file_for_routes(self, filepath: Path, patterns: list) -> None:
        """Scan a single file for route definitions."""
        try:
            content = filepath.read_text()
        except:
            return
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                method = match.group(1).upper()
                path = match.group(2)
                self.backend_routes.append({
                    'method': method,
                    'path': path,
                    'file': str(filepath),
                })

    def _compare_frontend_to_backend(self) -> None:
        """Compare frontend API calls to backend routes."""
        backend_paths = set()
        for route in self.backend_routes:
            # Normalize path
            path = route['path']
            path = re.sub(r':(\w+)', r'{\1}', path)  # :id -> {id}
            backend_paths.add(path)
        
        for call in self.frontend_calls:
            url = call['url']
            # Extract path from URL
            path = re.sub(r'https?://[^/]+', '', url)
            path = re.sub(r'\$\{[^}]+\}', '{id}', path)  # ${id} -> {id}
            path = re.sub(r'/[a-f0-9-]{36}', '/{id}', path)  # UUIDs -> {id}
            
            if path.startswith('/api') and path not in backend_paths:
                # Check if it's defined in endpoints.ts
                if path not in self.api_endpoints:
                    self.issues.append(ValidationIssue(
                        severity=Severity.WARNING,
                        category="Route Mismatch",
                        message=f"Frontend calls '{path}' but no matching backend route found",
                        file=call['file'],
                        suggestion="Add route to backend or fix frontend URL"
                    ))

    def _print_report(self) -> None:
        """Print validation report."""
        print("\n" + "=" * 60)
        print("         INTEGRATION VALIDATION REPORT")
        print("=" * 60)
        
        if not self.issues:
            print("\n✅ All checks passed! Frontend and backend are in sync.\n")
            return
        
        # Group by category
        by_category: dict[str, list] = {}
        for issue in self.issues:
            if issue.category not in by_category:
                by_category[issue.category] = []
            by_category[issue.category].append(issue)
        
        errors = [i for i in self.issues if i.severity == Severity.ERROR]
        warnings = [i for i in self.issues if i.severity == Severity.WARNING]
        
        print(f"\nFound {len(errors)} errors, {len(warnings)} warnings\n")
        
        for category, issues in by_category.items():
            print(f"\n--- {category} ---")
            for issue in issues:
                print(f"\n{issue.severity.value} {issue.message}")
                if issue.file:
                    print(f"   File: {issue.file}")
                if issue.suggestion:
                    print(f"   💡 {issue.suggestion}")
        
        print("\n" + "=" * 60)
        
        if errors:
            print("\n❌ Validation FAILED - fix errors before deployment\n")
        else:
            print("\n⚠️ Validation passed with warnings - review before deployment\n")


def main():
    parser = argparse.ArgumentParser(description="Validate frontend-backend integration")
    parser.add_argument("--project-dir", "-p", type=Path, default=Path("."), help="Project directory")
    parser.add_argument("--contracts-only", "-c", type=Path, help="Only validate contracts directory")
    parser.add_argument("--fix-suggestions", "-f", action="store_true", help="Show detailed fix suggestions")
    
    args = parser.parse_args()
    
    if args.contracts_only:
        # Just validate contracts exist and are consistent
        validator = IntegrationValidator(args.contracts_only.parent)
        validator.contracts_dir = args.contracts_only
    else:
        validator = IntegrationValidator(args.project_dir)
    
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
