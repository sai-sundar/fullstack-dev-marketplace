#!/usr/bin/env python3
"""
Capture design patterns from benchmark sites for comparison.

Usage:
    python benchmark_capture.py --domain recruitment
    python benchmark_capture.py --url http://localhost:5173 --compare recruitment
    python benchmark_capture.py --domain ecommerce --sites-only

This script uses Playwright to:
1. Navigate to benchmark sites
2. Extract design patterns (colors, typography, spacing, components)
3. Compare your site against benchmarks
4. Generate comparison report
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

# Check for playwright
try:
    from playwright.async_api import async_playwright, Page
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    print("Then: playwright install chromium")
    sys.exit(1)


# Domain configurations
DOMAINS = {
    "recruitment": {
        "name": "Recruitment / Job Search",
        "sites": [
            {"name": "LinkedIn Jobs", "url": "https://linkedin.com/jobs"},
            {"name": "Indeed", "url": "https://indeed.com"},
            {"name": "Glassdoor", "url": "https://glassdoor.com"},
            {"name": "Handshake", "url": "https://joinhandshake.com"},
            {"name": "Wellfound", "url": "https://wellfound.com"},
        ],
        "criteria": [
            {"name": "Information Hierarchy", "weight": 9},
            {"name": "Form Usability", "weight": 9},
            {"name": "Trust Signals", "weight": 8},
            {"name": "Progress Feedback", "weight": 8},
            {"name": "Mobile Experience", "weight": 7},
        ],
    },
    "ecommerce": {
        "name": "E-Commerce",
        "sites": [
            {"name": "Shopify Demo", "url": "https://themes.shopify.com"},
            {"name": "Amazon", "url": "https://amazon.com"},
        ],
        "criteria": [
            {"name": "Product Presentation", "weight": 9},
            {"name": "Checkout Friction", "weight": 10},
            {"name": "Trust Signals", "weight": 9},
            {"name": "Mobile Shopping", "weight": 8},
        ],
    },
    "saas-dashboard": {
        "name": "SaaS Dashboard",
        "sites": [
            {"name": "Linear", "url": "https://linear.app"},
            {"name": "Vercel", "url": "https://vercel.com"},
        ],
        "criteria": [
            {"name": "Information Density", "weight": 8},
            {"name": "Navigation Clarity", "weight": 9},
            {"name": "Action Accessibility", "weight": 8},
            {"name": "Performance Feel", "weight": 9},
        ],
    },
}


@dataclass
class DesignPattern:
    colors: list[str]
    typography: dict
    spacing: list[int]
    screenshots: list[str]


@dataclass
class BenchmarkResult:
    site_name: str
    url: str
    pattern: DesignPattern
    captured_at: str


async def extract_colors(page: Page) -> list[str]:
    """Extract dominant colors from page."""
    return await page.evaluate("""
        () => {
            const elements = document.querySelectorAll('*');
            const colors = new Map();
            
            elements.forEach(el => {
                const style = getComputedStyle(el);
                const bg = style.backgroundColor;
                const text = style.color;
                
                if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                    colors.set(bg, (colors.get(bg) || 0) + 1);
                }
                if (text) {
                    colors.set(text, (colors.get(text) || 0) + 1);
                }
            });
            
            return Array.from(colors.entries())
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10)
                .map(([color]) => color);
        }
    """)


async def extract_typography(page: Page) -> dict:
    """Extract typography patterns from page."""
    return await page.evaluate("""
        () => {
            const typography = {};
            const headings = ['h1', 'h2', 'h3', 'h4'];
            
            headings.forEach(tag => {
                const el = document.querySelector(tag);
                if (el) {
                    const style = getComputedStyle(el);
                    typography[tag] = {
                        fontFamily: style.fontFamily.split(',')[0].trim(),
                        fontSize: style.fontSize,
                        fontWeight: style.fontWeight,
                        lineHeight: style.lineHeight,
                    };
                }
            });
            
            const body = document.querySelector('p, .body, main');
            if (body) {
                const style = getComputedStyle(body);
                typography['body'] = {
                    fontFamily: style.fontFamily.split(',')[0].trim(),
                    fontSize: style.fontSize,
                    lineHeight: style.lineHeight,
                };
            }
            
            return typography;
        }
    """)


async def extract_spacing(page: Page) -> list[int]:
    """Extract common spacing values from page."""
    return await page.evaluate("""
        () => {
            const spacings = new Set();
            const elements = document.querySelectorAll('*');
            
            elements.forEach(el => {
                const style = getComputedStyle(el);
                ['margin', 'padding'].forEach(prop => {
                    ['Top', 'Right', 'Bottom', 'Left'].forEach(dir => {
                        const value = parseInt(style[prop + dir]);
                        if (value > 0 && value < 200) {
                            spacings.add(value);
                        }
                    });
                });
            });
            
            return Array.from(spacings).sort((a, b) => a - b).slice(0, 20);
        }
    """)


async def capture_site(
    page: Page, 
    name: str, 
    url: str, 
    output_dir: Path
) -> Optional[BenchmarkResult]:
    """Capture design patterns from a single site."""
    from datetime import datetime
    
    print(f"  📸 Capturing: {name}...")
    
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)  # Wait for dynamic content
        
        # Extract patterns
        colors = await extract_colors(page)
        typography = await extract_typography(page)
        spacing = await extract_spacing(page)
        
        # Take screenshot
        screenshot_path = output_dir / f"{name.lower().replace(' ', '-')}.png"
        await page.screenshot(path=str(screenshot_path), full_page=False)
        
        pattern = DesignPattern(
            colors=colors,
            typography=typography,
            spacing=spacing,
            screenshots=[str(screenshot_path)],
        )
        
        return BenchmarkResult(
            site_name=name,
            url=url,
            pattern=pattern,
            captured_at=datetime.now().isoformat(),
        )
        
    except Exception as e:
        print(f"  ⚠️ Failed to capture {name}: {e}")
        return None


async def capture_domain(domain_key: str, output_dir: Path) -> list[BenchmarkResult]:
    """Capture all benchmark sites for a domain."""
    domain = DOMAINS.get(domain_key)
    if not domain:
        print(f"Unknown domain: {domain_key}")
        print(f"Available domains: {', '.join(DOMAINS.keys())}")
        return []
    
    print(f"\n🎯 Capturing benchmarks for: {domain['name']}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        for site in domain["sites"]:
            result = await capture_site(page, site["name"], site["url"], output_dir)
            if result:
                results.append(result)
        
        await browser.close()
    
    # Save results
    results_file = output_dir / "benchmark_results.json"
    with open(results_file, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    
    print(f"\n✅ Captured {len(results)} sites")
    print(f"   Results saved to: {results_file}")
    
    return results


async def compare_site(
    url: str, 
    domain_key: str, 
    benchmark_dir: Path,
    output_dir: Path
) -> dict:
    """Compare a site against domain benchmarks."""
    domain = DOMAINS.get(domain_key)
    if not domain:
        print(f"Unknown domain: {domain_key}")
        return {}
    
    # Load benchmark results
    benchmark_file = benchmark_dir / "benchmark_results.json"
    if not benchmark_file.exists():
        print(f"No benchmarks found for {domain_key}. Run capture first.")
        return {}
    
    with open(benchmark_file) as f:
        benchmarks = json.load(f)
    
    print(f"\n🔍 Comparing {url} against {domain['name']} benchmarks...")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        
        # Capture your site
        your_result = await capture_site(page, "Your Site", url, output_dir)
        await browser.close()
    
    if not your_result:
        print("Failed to capture your site")
        return {}
    
    # Compare patterns
    comparison = {
        "your_site": asdict(your_result),
        "benchmarks": benchmarks,
        "analysis": analyze_patterns(your_result.pattern, benchmarks, domain["criteria"]),
    }
    
    # Save comparison
    comparison_file = output_dir / "comparison_report.json"
    with open(comparison_file, "w") as f:
        json.dump(comparison, f, indent=2)
    
    # Print summary
    print_comparison_summary(comparison)
    
    return comparison


def analyze_patterns(
    your_pattern: DesignPattern, 
    benchmarks: list[dict],
    criteria: list[dict]
) -> dict:
    """Analyze patterns and generate scores."""
    analysis = {
        "overall_score": 0,
        "criteria_scores": [],
        "recommendations": [],
    }
    
    # Color analysis
    your_colors = set(your_pattern.colors)
    benchmark_colors = set()
    for b in benchmarks:
        benchmark_colors.update(b.get("pattern", {}).get("colors", []))
    
    # Typography analysis
    your_typography = your_pattern.typography
    
    # Simple scoring based on presence of key elements
    scores = []
    
    # Check body font size
    body_font = your_typography.get("body", {})
    body_size = int(body_font.get("fontSize", "14px").replace("px", ""))
    if body_size >= 16:
        scores.append({"criterion": "Typography", "score": 9, "note": "Good body font size"})
    elif body_size >= 14:
        scores.append({"criterion": "Typography", "score": 6, "note": "Consider larger body font"})
        analysis["recommendations"].append("Increase body font size to 16px for better readability")
    else:
        scores.append({"criterion": "Typography", "score": 3, "note": "Body font too small"})
        analysis["recommendations"].append("Body font size is too small. Increase to at least 16px")
    
    # Check color variety
    if len(your_colors) >= 5:
        scores.append({"criterion": "Color System", "score": 8, "note": "Good color variety"})
    else:
        scores.append({"criterion": "Color System", "score": 5, "note": "Limited color palette"})
        analysis["recommendations"].append("Consider expanding your color palette")
    
    # Check spacing consistency
    spacing = your_pattern.spacing
    if len(spacing) > 0:
        # Check if spacing follows a scale (4px, 8px, 16px, etc.)
        base_4 = [s for s in spacing if s % 4 == 0]
        if len(base_4) / len(spacing) > 0.7:
            scores.append({"criterion": "Spacing System", "score": 9, "note": "Consistent 4px grid"})
        else:
            scores.append({"criterion": "Spacing System", "score": 6, "note": "Inconsistent spacing"})
            analysis["recommendations"].append("Standardize spacing to a 4px or 8px grid")
    
    analysis["criteria_scores"] = scores
    analysis["overall_score"] = sum(s["score"] for s in scores) / len(scores) if scores else 0
    
    return analysis


def print_comparison_summary(comparison: dict) -> None:
    """Print a human-readable comparison summary."""
    print("\n" + "=" * 60)
    print("              DESIGN BENCHMARK COMPARISON")
    print("=" * 60)
    
    analysis = comparison.get("analysis", {})
    overall = analysis.get("overall_score", 0)
    
    print(f"\n📊 Overall Score: {overall:.1f}/10")
    print("\n" + "-" * 60)
    print("Criteria Breakdown:")
    
    for score in analysis.get("criteria_scores", []):
        icon = "✅" if score["score"] >= 7 else "⚠️" if score["score"] >= 5 else "❌"
        print(f"  {icon} {score['criterion']}: {score['score']}/10 - {score['note']}")
    
    recommendations = analysis.get("recommendations", [])
    if recommendations:
        print("\n" + "-" * 60)
        print("📝 Recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")
    
    print("\n" + "=" * 60)


def list_domains() -> None:
    """List available domains."""
    print("\nAvailable Domains:")
    print("-" * 40)
    for key, domain in DOMAINS.items():
        print(f"\n{key}:")
        print(f"  Name: {domain['name']}")
        print(f"  Sites: {len(domain['sites'])}")
        for site in domain["sites"]:
            print(f"    • {site['name']}")


def main():
    parser = argparse.ArgumentParser(description="Capture and compare design benchmarks")
    parser.add_argument("--domain", "-d", help="Domain to benchmark (e.g., recruitment)")
    parser.add_argument("--url", "-u", help="Your site URL to compare")
    parser.add_argument("--compare", "-c", help="Domain to compare against")
    parser.add_argument("--output", "-o", default="./benchmarks", help="Output directory")
    parser.add_argument("--list", "-l", action="store_true", help="List available domains")
    parser.add_argument("--sites-only", action="store_true", help="Only list sites, don't capture")
    
    args = parser.parse_args()
    
    if args.list:
        list_domains()
        return
    
    output_dir = Path(args.output)
    
    if args.domain:
        if args.sites_only:
            domain = DOMAINS.get(args.domain)
            if domain:
                print(f"\nBenchmark sites for {domain['name']}:")
                for site in domain["sites"]:
                    print(f"  • {site['name']}: {site['url']}")
            return
        
        domain_output = output_dir / args.domain
        asyncio.run(capture_domain(args.domain, domain_output))
    
    elif args.url and args.compare:
        benchmark_dir = output_dir / args.compare
        compare_output = output_dir / "comparison"
        asyncio.run(compare_site(args.url, args.compare, benchmark_dir, compare_output))
    
    else:
        parser.print_help()
        print("\n\nExamples:")
        print("  python benchmark_capture.py --list")
        print("  python benchmark_capture.py --domain recruitment")
        print("  python benchmark_capture.py --url http://localhost:5173 --compare recruitment")


if __name__ == "__main__":
    main()
