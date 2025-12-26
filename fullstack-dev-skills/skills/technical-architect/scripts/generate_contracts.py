#!/usr/bin/env python3
"""
Generate binding contracts for a project.

Usage:
    python generate_contracts.py --interactive
    python generate_contracts.py --from-spec spec.yaml --output ./contracts
    python generate_contracts.py --validate ./contracts

This script generates:
- database.sql (complete schema)
- types.ts (TypeScript interfaces)
- endpoints.ts (API endpoint constants)
- validation.ts (Zod schemas)
- errors.ts (error codes)
"""

import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def generate_database_sql(entities: list[dict], output_dir: Path) -> None:
    """Generate database.sql from entity definitions."""
    
    sql_parts = [
        f"""-- ============================================
-- DATABASE CONTRACT
-- Generated: {datetime.now().isoformat()}
-- Version: 1.0.0
-- ============================================
-- IMPORTANT: Execute this EXACTLY as written.
-- Column names MUST match types.ts field names.
-- ============================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- PROFILES (extends Supabase auth.users)
-- ============================================
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
"""
    ]
    
    for entity in entities:
        name = entity['name']
        table_name = entity.get('table_name', f"{name.lower()}s")
        columns = entity.get('columns', [])
        
        col_defs = []
        for col in columns:
            col_def = f"  {col['name']} {col['type']}"
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            if col.get('default'):
                col_def += f" DEFAULT {col['default']}"
            if col.get('not_null'):
                col_def += " NOT NULL"
            if col.get('references'):
                col_def += f" REFERENCES {col['references']} ON DELETE CASCADE"
            if col.get('check'):
                col_def += f" CHECK ({col['check']})"
            col_defs.append(col_def)
        
        sql_parts.append(f"""
-- ============================================
-- {name.upper()}
-- ============================================
CREATE TABLE public.{table_name} (
{',\n'.join(col_defs)}
);
""")
    
    # Add indexes
    sql_parts.append("""
-- ============================================
-- INDEXES
-- ============================================
""")
    
    for entity in entities:
        table_name = entity.get('table_name', f"{entity['name'].lower()}s")
        for col in entity.get('columns', []):
            if col.get('index'):
                sql_parts.append(f"CREATE INDEX idx_{table_name}_{col['name']} ON public.{table_name}({col['name']});")
    
    # Add RLS
    sql_parts.append("""

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
""")
    
    for entity in entities:
        table_name = entity.get('table_name', f"{entity['name'].lower()}s")
        sql_parts.append(f"ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY;")
    
    # Add triggers
    sql_parts.append("""

-- ============================================
-- TRIGGERS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""")
    
    for entity in entities:
        table_name = entity.get('table_name', f"{entity['name'].lower()}s")
        if any(col['name'] == 'updated_at' for col in entity.get('columns', [])):
            sql_parts.append(f"""
CREATE TRIGGER {table_name}_updated_at BEFORE UPDATE ON public.{table_name}
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
""")
    
    with open(output_dir / 'database.sql', 'w') as f:
        f.write('\n'.join(sql_parts))
    
    print(f"  ✓ Generated database.sql")


def generate_types_ts(entities: list[dict], endpoints: list[dict], output_dir: Path) -> None:
    """Generate types.ts from entity and endpoint definitions."""
    
    ts_parts = [
        f"""// ============================================
// TYPES CONTRACT
// Generated: {datetime.now().isoformat()}
// Version: 1.0.0
// ============================================
// IMPORTANT: Field names MUST match database.sql column names exactly.
// Both frontend and backend MUST import from this file.
// ============================================

"""
    ]
    
    # Type mapping
    type_map = {
        'UUID': 'string',
        'TEXT': 'string',
        'INTEGER': 'number',
        'BIGINT': 'number',
        'BOOLEAN': 'boolean',
        'TIMESTAMPTZ': 'string',
        'JSONB': 'Record<string, unknown>',
    }
    
    # Generate entity interfaces
    ts_parts.append("// ============================================\n// DATABASE ENTITIES\n// ============================================\n")
    
    for entity in entities:
        name = entity['name']
        columns = entity.get('columns', [])
        
        fields = []
        for col in columns:
            ts_type = type_map.get(col['type'].split('(')[0].upper(), 'unknown')
            nullable = ' | null' if not col.get('not_null') and not col.get('primary_key') else ''
            fields.append(f"  {col['name']}: {ts_type}{nullable};")
        
        ts_parts.append(f"""
export interface {name} {{
{chr(10).join(fields)}
}}
""")
    
    # Generate request/response types
    ts_parts.append("\n// ============================================\n// API REQUEST/RESPONSE TYPES\n// ============================================\n")
    
    for endpoint in endpoints:
        if endpoint.get('request_type'):
            ts_parts.append(f"\nexport interface {endpoint['request_type']} {{\n  // TODO: Define request fields\n}}\n")
        if endpoint.get('response_type'):
            ts_parts.append(f"\nexport interface {endpoint['response_type']} {{\n  // TODO: Define response fields\n}}\n")
    
    # Add common types
    ts_parts.append("""
// ============================================
// PAGINATION
// ============================================

export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

// ============================================
// API RESPONSE WRAPPER
// ============================================

export interface ApiResponse<T> {
  success: true;
  data: T;
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}

export type ApiResult<T> = ApiResponse<T> | ApiError;
""")
    
    with open(output_dir / 'types.ts', 'w') as f:
        f.write(''.join(ts_parts))
    
    print(f"  ✓ Generated types.ts")


def generate_endpoints_ts(endpoints: list[dict], output_dir: Path) -> None:
    """Generate endpoints.ts from endpoint definitions."""
    
    ts_content = f"""// ============================================
// ENDPOINTS CONTRACT
// Generated: {datetime.now().isoformat()}
// Version: 1.0.0
// ============================================
// IMPORTANT: Frontend and backend MUST use these constants.
// Never hardcode endpoint strings.
// ============================================

export const API_VERSION = 'v1';
export const API_BASE = `/api/${{API_VERSION}}`;

export const ENDPOINTS = {{
"""
    
    # Group endpoints by resource
    resources: dict[str, list] = {}
    for ep in endpoints:
        resource = ep.get('resource', 'OTHER')
        if resource not in resources:
            resources[resource] = []
        resources[resource].append(ep)
    
    for resource, eps in resources.items():
        ts_content += f"\n  // {resource}\n  {resource}: {{\n"
        for ep in eps:
            name = ep['name']
            path = ep['path']
            if ':id' in path or '{id}' in path:
                clean_path = path.replace(':id', '${id}').replace('{id}', '${id}')
                ts_content += f"    {name}: (id: string) => `${{API_BASE}}{clean_path}`,\n"
            else:
                ts_content += f"    {name}: `${{API_BASE}}{path}`,\n"
        ts_content += "  },\n"
    
    ts_content += """} as const;

// Type helper for endpoint parameters
export type EndpointWithParam = (id: string) => string;
"""
    
    with open(output_dir / 'endpoints.ts', 'w') as f:
        f.write(ts_content)
    
    print(f"  ✓ Generated endpoints.ts")


def generate_validation_ts(entities: list[dict], output_dir: Path) -> None:
    """Generate validation.ts with Zod schemas."""
    
    ts_content = f"""// ============================================
// VALIDATION CONTRACT
// Generated: {datetime.now().isoformat()}
// Version: 1.0.0
// ============================================
// IMPORTANT: Use these schemas for BOTH client and server validation.
// ============================================

import {{ z }} from 'zod';

// ============================================
// ENTITY SCHEMAS
// ============================================
"""
    
    type_to_zod = {
        'UUID': 'z.string().uuid()',
        'TEXT': 'z.string()',
        'INTEGER': 'z.number().int()',
        'BIGINT': 'z.number().int()',
        'BOOLEAN': 'z.boolean()',
        'TIMESTAMPTZ': 'z.string().datetime()',
        'JSONB': 'z.record(z.string(), z.unknown())',
    }
    
    for entity in entities:
        name = entity['name']
        columns = entity.get('columns', [])
        
        fields = []
        for col in columns:
            zod_type = type_to_zod.get(col['type'].split('(')[0].upper(), 'z.unknown()')
            if not col.get('not_null') and not col.get('primary_key'):
                zod_type += '.nullable()'
            fields.append(f"  {col['name']}: {zod_type},")
        
        ts_content += f"""
export const {name}Schema = z.object({{
{chr(10).join(fields)}
}});
"""
    
    ts_content += """
// ============================================
// PAGINATION
// ============================================

export const PaginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
});

// ============================================
// TYPE EXPORTS
// ============================================
"""
    
    for entity in entities:
        name = entity['name']
        ts_content += f"\nexport type {name}Input = z.infer<typeof {name}Schema>;"
    
    with open(output_dir / 'validation.ts', 'w') as f:
        f.write(ts_content)
    
    print(f"  ✓ Generated validation.ts")


def generate_errors_ts(output_dir: Path) -> None:
    """Generate errors.ts with error codes."""
    
    ts_content = f"""// ============================================
// ERROR CONTRACT
// Generated: {datetime.now().isoformat()}
// Version: 1.0.0
// ============================================

export const ERROR_CODES = {{
  // Authentication
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',

  // Validation
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_INPUT: 'INVALID_INPUT',

  // Resources
  NOT_FOUND: 'NOT_FOUND',

  // Rate limiting
  RATE_LIMITED: 'RATE_LIMITED',

  // Server
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
}} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];

export const HTTP_STATUS: Record<ErrorCode, number> = {{
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  TOKEN_EXPIRED: 401,
  VALIDATION_ERROR: 400,
  INVALID_INPUT: 400,
  NOT_FOUND: 404,
  RATE_LIMITED: 429,
  INTERNAL_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
}};

export const ERROR_MESSAGES: Record<ErrorCode, string> = {{
  UNAUTHORIZED: 'Authentication required',
  FORBIDDEN: 'You do not have permission to access this resource',
  TOKEN_EXPIRED: 'Your session has expired, please log in again',
  VALIDATION_ERROR: 'Invalid input data',
  INVALID_INPUT: 'Invalid input provided',
  NOT_FOUND: 'Resource not found',
  RATE_LIMITED: 'Too many requests, please try again later',
  INTERNAL_ERROR: 'An unexpected error occurred',
  SERVICE_UNAVAILABLE: 'Service temporarily unavailable',
}};
"""
    
    with open(output_dir / 'errors.ts', 'w') as f:
        f.write(ts_content)
    
    print(f"  ✓ Generated errors.ts")


def interactive_mode() -> tuple[list[dict], list[dict]]:
    """Interactively define entities and endpoints."""
    
    print("\n=== Contract Generator ===\n")
    print("Define your entities (database tables) and endpoints.\n")
    
    entities = []
    endpoints = []
    
    # Define entities
    print("--- ENTITIES ---")
    print("Enter entity names (e.g., 'CV', 'Analysis'). Empty to finish.\n")
    
    while True:
        name = input("Entity name (or empty to finish): ").strip()
        if not name:
            break
        
        name = name[0].upper() + name[1:]  # Capitalize
        table_name = input(f"  Table name [{name.lower()}s]: ").strip() or f"{name.lower()}s"
        
        print(f"  Define columns for {name}:")
        print("  Format: name:type (e.g., 'title:TEXT', 'score:INTEGER')")
        print("  Add '!' for NOT NULL, '*' for PRIMARY KEY, '?' for nullable")
        print("  Empty line to finish columns.\n")
        
        columns = [
            {'name': 'id', 'type': 'UUID', 'primary_key': True, 'default': 'uuid_generate_v4()'},
        ]
        
        while True:
            col_input = input("    Column: ").strip()
            if not col_input:
                break
            
            parts = col_input.split(':')
            if len(parts) != 2:
                print("    Invalid format. Use 'name:TYPE'")
                continue
            
            col_name = parts[0].strip().rstrip('!*?')
            col_type = parts[1].strip().upper()
            
            col = {
                'name': col_name,
                'type': col_type,
                'not_null': '!' in parts[0] or '*' in parts[0],
                'primary_key': '*' in parts[0],
            }
            columns.append(col)
        
        # Add timestamps
        columns.extend([
            {'name': 'created_at', 'type': 'TIMESTAMPTZ', 'default': 'now()', 'not_null': True},
            {'name': 'updated_at', 'type': 'TIMESTAMPTZ', 'default': 'now()', 'not_null': True},
        ])
        
        entities.append({
            'name': name,
            'table_name': table_name,
            'columns': columns,
        })
        print(f"  ✓ Added entity: {name}\n")
    
    # Define endpoints
    print("\n--- ENDPOINTS ---")
    print("Define API endpoints. Format: METHOD /path")
    print("Example: POST /cv/upload")
    print("Empty to finish.\n")
    
    while True:
        ep_input = input("Endpoint (e.g., 'POST /cv/upload'): ").strip()
        if not ep_input:
            break
        
        parts = ep_input.split(' ', 1)
        if len(parts) != 2:
            print("Invalid format. Use 'METHOD /path'")
            continue
        
        method = parts[0].upper()
        path = parts[1]
        
        # Infer resource from path
        resource = path.split('/')[1].upper() if '/' in path else 'OTHER'
        name = path.split('/')[-1].upper().replace('-', '_').replace(':ID', '')
        if not name or name == resource.lower():
            name = method
        
        endpoints.append({
            'method': method,
            'path': path,
            'resource': resource,
            'name': name,
        })
        print(f"  ✓ Added: {method} {path}\n")
    
    return entities, endpoints


def validate_contracts(contracts_dir: Path) -> bool:
    """Validate existing contracts for consistency."""
    
    print(f"\n🔍 Validating contracts in: {contracts_dir}\n")
    
    required_files = ['database.sql', 'types.ts', 'endpoints.ts', 'validation.ts', 'errors.ts']
    errors = []
    warnings = []
    
    # Check required files exist
    for f in required_files:
        if not (contracts_dir / f).exists():
            errors.append(f"Missing required file: {f}")
    
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
        return False
    
    # Read files
    database_sql = (contracts_dir / 'database.sql').read_text()
    types_ts = (contracts_dir / 'types.ts').read_text()
    
    # Extract table names from SQL
    import re
    sql_tables = set(re.findall(r'CREATE TABLE public\.(\w+)', database_sql))
    
    # Extract interface names from TypeScript
    ts_interfaces = set(re.findall(r'export interface (\w+)', types_ts))
    
    # Check each table has a corresponding interface
    for table in sql_tables:
        # Convert table name to expected interface name (e.g., cvs -> CV, profiles -> Profile)
        expected_interface = table.rstrip('s').title()
        if expected_interface not in ts_interfaces and table.title() not in ts_interfaces:
            warnings.append(f"Table '{table}' may not have corresponding TypeScript interface")
    
    # Extract column names from SQL
    sql_columns: dict[str, set] = {}
    current_table = None
    for line in database_sql.split('\n'):
        table_match = re.match(r'CREATE TABLE public\.(\w+)', line)
        if table_match:
            current_table = table_match.group(1)
            sql_columns[current_table] = set()
        elif current_table and re.match(r'\s+(\w+)\s+', line):
            col_match = re.match(r'\s+(\w+)\s+', line)
            if col_match:
                sql_columns[current_table].add(col_match.group(1))
    
    # Print results
    print(f"  Found {len(sql_tables)} tables in database.sql")
    print(f"  Found {len(ts_interfaces)} interfaces in types.ts")
    
    if warnings:
        print("\n  ⚠️ Warnings:")
        for w in warnings:
            print(f"    - {w}")
    
    if not errors and not warnings:
        print("\n  ✅ All contracts valid!")
        return True
    
    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description="Generate binding contracts")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--output", "-o", type=Path, default=Path("./contracts"), help="Output directory")
    parser.add_argument("--validate", "-v", type=Path, help="Validate existing contracts directory")
    
    args = parser.parse_args()
    
    if args.validate:
        success = validate_contracts(args.validate)
        exit(0 if success else 1)
    
    if args.interactive:
        entities, endpoints = interactive_mode()
    else:
        # Default example entities for recruitment app
        entities = [
            {
                'name': 'CV',
                'table_name': 'cvs',
                'columns': [
                    {'name': 'id', 'type': 'UUID', 'primary_key': True, 'default': 'uuid_generate_v4()'},
                    {'name': 'user_id', 'type': 'UUID', 'not_null': True, 'references': 'auth.users(id)', 'index': True},
                    {'name': 'file_url', 'type': 'TEXT', 'not_null': True},
                    {'name': 'original_filename', 'type': 'TEXT', 'not_null': True},
                    {'name': 'file_size_bytes', 'type': 'INTEGER', 'not_null': True},
                    {'name': 'target_role', 'type': 'TEXT'},
                    {'name': 'status', 'type': 'TEXT', 'not_null': True, 'default': "'uploaded'"},
                    {'name': 'created_at', 'type': 'TIMESTAMPTZ', 'default': 'now()', 'not_null': True},
                    {'name': 'updated_at', 'type': 'TIMESTAMPTZ', 'default': 'now()', 'not_null': True},
                ],
            },
        ]
        endpoints = [
            {'method': 'GET', 'path': '/cv', 'resource': 'CV', 'name': 'LIST'},
            {'method': 'POST', 'path': '/cv/upload', 'resource': 'CV', 'name': 'UPLOAD'},
            {'method': 'GET', 'path': '/cv/:id', 'resource': 'CV', 'name': 'GET'},
            {'method': 'POST', 'path': '/cv/:id/analyze', 'resource': 'CV', 'name': 'ANALYZE'},
        ]
    
    # Create output directory
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📝 Generating contracts in: {output_dir}\n")
    
    # Generate all files
    generate_database_sql(entities, output_dir)
    generate_types_ts(entities, endpoints, output_dir)
    generate_endpoints_ts(endpoints, output_dir)
    generate_validation_ts(entities, output_dir)
    generate_errors_ts(output_dir)
    
    print(f"\n✅ Generated {len(list(output_dir.glob('*')))} contract files")
    print(f"\nNext steps:")
    print(f"  1. Review and customize the generated files")
    print(f"  2. Copy to packages/shared/src/contracts/")
    print(f"  3. Import from '@app/shared/contracts' in both frontend and backend")


if __name__ == "__main__":
    main()
