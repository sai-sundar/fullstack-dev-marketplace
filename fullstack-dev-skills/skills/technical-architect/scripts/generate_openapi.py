#!/usr/bin/env python3
"""
Generate OpenAPI specification from route definitions.

Usage:
    python generate_openapi.py --routes routes.yaml --output openapi.yaml
    python generate_openapi.py --interactive

This script helps create OpenAPI specs by:
1. Reading route definitions from a simplified YAML format
2. Generating full OpenAPI 3.0 specification
3. Optionally generating TypeScript types
"""

import argparse
import yaml
import json
from pathlib import Path
from datetime import datetime


def create_base_spec(title: str, version: str, description: str = "") -> dict:
    """Create base OpenAPI specification structure."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": title,
            "version": version,
            "description": description,
        },
        "servers": [
            {"url": "http://localhost:3001/api", "description": "Development"},
            {"url": "https://api.example.com", "description": "Production"},
        ],
        "paths": {},
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            },
            "schemas": {},
            "responses": {
                "ValidationError": {
                    "description": "Validation failed",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"}
                        }
                    },
                },
                "Unauthorized": {
                    "description": "Authentication required",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"}
                        }
                    },
                },
                "NotFound": {
                    "description": "Resource not found",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"}
                        }
                    },
                },
            },
        },
    }


def add_common_schemas(spec: dict) -> None:
    """Add common schema definitions."""
    spec["components"]["schemas"]["Error"] = {
        "type": "object",
        "properties": {
            "error": {"type": "string"},
            "code": {"type": "string"},
            "details": {"type": "object"},
        },
    }
    
    spec["components"]["schemas"]["Pagination"] = {
        "type": "object",
        "properties": {
            "page": {"type": "integer"},
            "limit": {"type": "integer"},
            "total": {"type": "integer"},
            "pages": {"type": "integer"},
        },
    }


def generate_crud_routes(resource: str, schema: dict, spec: dict) -> None:
    """Generate standard CRUD routes for a resource."""
    resource_lower = resource.lower()
    resource_plural = f"{resource_lower}s"
    
    # Add schema
    spec["components"]["schemas"][resource] = schema
    
    # Create input schema (without id and timestamps)
    create_schema = {
        "type": "object",
        "required": [k for k, v in schema.get("properties", {}).items() 
                    if k not in ["id", "createdAt", "updatedAt"] and 
                    schema.get("required") and k in schema["required"]],
        "properties": {k: v for k, v in schema.get("properties", {}).items()
                      if k not in ["id", "createdAt", "updatedAt"]},
    }
    spec["components"]["schemas"][f"Create{resource}Input"] = create_schema
    
    # Paginated response
    spec["components"]["schemas"][f"Paginated{resource}s"] = {
        "type": "object",
        "properties": {
            "data": {
                "type": "array",
                "items": {"$ref": f"#/components/schemas/{resource}"},
            },
            "pagination": {"$ref": "#/components/schemas/Pagination"},
        },
    }
    
    # List endpoint
    spec["paths"][f"/{resource_plural}"] = {
        "get": {
            "summary": f"List all {resource_plural}",
            "operationId": f"list{resource}s",
            "tags": [resource],
            "parameters": [
                {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20}},
            ],
            "responses": {
                "200": {
                    "description": f"Paginated list of {resource_plural}",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/Paginated{resource}s"}
                        }
                    },
                }
            },
        },
        "post": {
            "summary": f"Create a {resource_lower}",
            "operationId": f"create{resource}",
            "tags": [resource],
            "security": [{"bearerAuth": []}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/Create{resource}Input"}
                    }
                },
            },
            "responses": {
                "201": {
                    "description": f"{resource} created",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{resource}"}
                        }
                    },
                },
                "400": {"$ref": "#/components/responses/ValidationError"},
                "401": {"$ref": "#/components/responses/Unauthorized"},
            },
        },
    }
    
    # Single resource endpoints
    spec["paths"][f"/{resource_plural}/{{id}}"] = {
        "get": {
            "summary": f"Get a {resource_lower} by ID",
            "operationId": f"get{resource}",
            "tags": [resource],
            "parameters": [
                {"name": "id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}
            ],
            "responses": {
                "200": {
                    "description": f"{resource} details",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{resource}"}
                        }
                    },
                },
                "404": {"$ref": "#/components/responses/NotFound"},
            },
        },
        "put": {
            "summary": f"Update a {resource_lower}",
            "operationId": f"update{resource}",
            "tags": [resource],
            "security": [{"bearerAuth": []}],
            "parameters": [
                {"name": "id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/Create{resource}Input"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": f"{resource} updated",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{resource}"}
                        }
                    },
                },
                "400": {"$ref": "#/components/responses/ValidationError"},
                "401": {"$ref": "#/components/responses/Unauthorized"},
                "404": {"$ref": "#/components/responses/NotFound"},
            },
        },
        "delete": {
            "summary": f"Delete a {resource_lower}",
            "operationId": f"delete{resource}",
            "tags": [resource],
            "security": [{"bearerAuth": []}],
            "parameters": [
                {"name": "id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}
            ],
            "responses": {
                "204": {"description": f"{resource} deleted"},
                "401": {"$ref": "#/components/responses/Unauthorized"},
                "404": {"$ref": "#/components/responses/NotFound"},
            },
        },
    }


def interactive_mode() -> dict:
    """Interactively build an OpenAPI spec."""
    print("\n=== OpenAPI Specification Generator ===\n")
    
    title = input("API Title [MyApp API]: ").strip() or "MyApp API"
    version = input("Version [1.0.0]: ").strip() or "1.0.0"
    description = input("Description: ").strip()
    
    spec = create_base_spec(title, version, description)
    add_common_schemas(spec)
    
    print("\n--- Define Resources ---")
    print("For each resource, we'll generate CRUD endpoints.")
    print("Enter resource names (e.g., 'Post', 'User'). Empty to finish.\n")
    
    while True:
        resource = input("Resource name (or empty to finish): ").strip()
        if not resource:
            break
        
        resource = resource[0].upper() + resource[1:]  # Capitalize
        print(f"\nDefining schema for {resource}:")
        
        properties = {}
        required = []
        
        # Add standard fields
        properties["id"] = {"type": "string", "format": "uuid"}
        properties["createdAt"] = {"type": "string", "format": "date-time"}
        properties["updatedAt"] = {"type": "string", "format": "date-time"}
        
        print("Add fields (name:type, e.g., 'title:string', 'count:integer')")
        print("Available types: string, integer, number, boolean, array")
        print("Empty line to finish fields.\n")
        
        while True:
            field_input = input("  Field (name:type): ").strip()
            if not field_input:
                break
            
            if ":" not in field_input:
                print("  Invalid format. Use 'name:type'")
                continue
            
            name, field_type = field_input.split(":", 1)
            name = name.strip()
            field_type = field_type.strip().lower()
            
            type_map = {
                "string": {"type": "string"},
                "text": {"type": "string"},
                "integer": {"type": "integer"},
                "int": {"type": "integer"},
                "number": {"type": "number"},
                "float": {"type": "number"},
                "boolean": {"type": "boolean"},
                "bool": {"type": "boolean"},
                "array": {"type": "array", "items": {"type": "string"}},
                "uuid": {"type": "string", "format": "uuid"},
                "email": {"type": "string", "format": "email"},
                "date": {"type": "string", "format": "date"},
                "datetime": {"type": "string", "format": "date-time"},
            }
            
            if field_type in type_map:
                properties[name] = type_map[field_type]
                is_required = input(f"    Is '{name}' required? [y/N]: ").strip().lower()
                if is_required == "y":
                    required.append(name)
            else:
                print(f"  Unknown type: {field_type}")
        
        schema = {
            "type": "object",
            "required": required + ["id", "createdAt"],
            "properties": properties,
        }
        
        generate_crud_routes(resource, schema, spec)
        print(f"✓ Generated CRUD endpoints for {resource}\n")
    
    return spec


def main():
    parser = argparse.ArgumentParser(description="Generate OpenAPI specification")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--routes", type=Path, help="Routes definition YAML file")
    parser.add_argument("--output", "-o", type=Path, default=Path("openapi.yaml"), help="Output file")
    
    args = parser.parse_args()
    
    if args.interactive:
        spec = interactive_mode()
    elif args.routes:
        with open(args.routes) as f:
            routes_def = yaml.safe_load(f)
        
        spec = create_base_spec(
            routes_def.get("title", "API"),
            routes_def.get("version", "1.0.0"),
            routes_def.get("description", ""),
        )
        add_common_schemas(spec)
        
        for resource in routes_def.get("resources", []):
            generate_crud_routes(resource["name"], resource["schema"], spec)
    else:
        print("Specify --interactive or --routes <file>")
        return
    
    # Write output
    output_path = args.output
    with open(output_path, "w") as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n✓ OpenAPI spec written to: {output_path}")
    print("\nNext steps:")
    print("  1. Review and customize the generated spec")
    print("  2. Generate TypeScript types: npx openapi-typescript openapi.yaml -o types/api.ts")
    print("  3. Use with Swagger UI for documentation")


if __name__ == "__main__":
    main()
