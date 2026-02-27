#!/usr/bin/env python3
"""Test script for new website categorizer integration."""

from backend.process_monitor import ProcessMonitor
from backend.website_categorizer import get_website_categorizer
from backend.website_cache import get_website_cache

print("=" * 60)
print("🧪 Testing Website Categorizer Integration")
print("=" * 60)

# Test 1: Load website categorizer
print("\n✅ Test 1: Loading website categorizer...")
categorizer = get_website_categorizer()
print(f"   - Dictionary loaded: {len(categorizer.dictionary)} domains")
print(f"   - Gemini available: {categorizer.gemini.is_available()}")

# Test 2: Test domain extraction
print("\n✅ Test 2: Testing domain extraction...")
test_titles = [
    "GitHub - user/repo",
    "Stack Overflow - how to...",
    "Netflix - Watch Movies",
    "Discord | Server Name"
]
for title in test_titles:
    domain = categorizer.extract_domain(title)
    print(f"   - '{title}' → {domain}")

# Test 3: Test synchronous categorization
print("\n✅ Test 3: Testing synchronous categorization...")
test_domains = ["github.com", "netflix.com", "unknown-site.xyz"]
results = categorizer.batch_categorize_sync(test_domains)
for domain, (category, confidence, source) in results.items():
    print(f"   - {domain} → {category} ({confidence:.2f}, {source})")

# Test 4: Test cache
print("\n✅ Test 4: Testing website cache...")
cache = get_website_cache()
cache_stats = cache.get_stats()
print(f"   - Total cached: {cache_stats.get('total_cached', 0)}")
print(f"   - By source: {cache_stats.get('by_source', {})}")

# Test 5: Test ProcessMonitor integration
print("\n✅ Test 5: Testing ProcessMonitor with new categorizer...")
pm = ProcessMonitor()
main_procs = pm.get_main_processes()
print(f"   - Found {len(main_procs)} main processes")

if main_procs:
    # Show first browser process if any
    browser_procs = [p for p in main_procs if p.get('domain')]
    if browser_procs:
        proc = browser_procs[0]
        print(f"\n   📌 Sample Browser Process:")
        print(f"      Name: {proc['name']}")
        print(f"      Domain: {proc.get('domain', 'N/A')}")
        print(f"      Category: {proc['category']}")
        print(f"      Window Title: {proc.get('window_title', 'N/A')[:60]}")
        print(f"      Source: {proc.get('categorization_source', 'N/A')}")
        print(f"      Confidence: {proc.get('domain_confidence', 0):.2f}")
    elif main_procs:
        proc = main_procs[0]
        print(f"\n   📌 Sample Process (non-browser):")
        print(f"      Name: {proc['name']}")
        print(f"      Category: {proc['category']}")
        print(f"      Memory: {proc['memory_mb']}MB")
        print(f"      CPU: {proc['cpu_percent']}%")

print("\n" + "=" * 60)
print("✨ All integration tests completed successfully!")
print("=" * 60)
