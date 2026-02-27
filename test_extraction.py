#!/usr/bin/env python3
"""Test domain extraction with new improved logic."""

from client.window_parser import WindowTitleParser

print("\n" + "="*70)
print("Testing Improved Domain Extraction")
print("="*70 + "\n")

test_cases = [
    ("Integer Break - LeetCode - Google Chrome", "leetcode"),
    ("Wolves vs Aston Villa Live video streaming | Premier League", "premier"),
    ("Google Gemini - Google Chrome", "gemini"),
    ("WEAVE-DB Progression Tracker - Google Sheets - Google Chrome", "weave"),
    ("(59) FastAPI for Machine Learning | CampusX - YouTube - Google Chrome", "fastapi"),
    ("(59) Greedy Algorithm Playlist | Language Independent Series - YouTube - Google Chrome", "greedy"),
    ("Productivity Tracker - Google Chrome", "productivity"),
    ("GitHub - user/repo", "github"),
    ("Gmail - Sign in", "gmail"),
    ("localhost:3000 - React App", "localhost"),
    ("Claude 3.5 Sonnet", "claude"),
]

print(f"{'Title':<60} {'Extracted':<15} {'Status':<10}")
print("-" * 85)

for title, expected_contains in test_cases:
    extracted = WindowTitleParser.extract_domain_from_title(title)
    contains_expected = expected_contains.lower() in (extracted or "").lower()
    status = "✅" if contains_expected else "⚠️"
    
    extracted_display = extracted[:14] if extracted else "None"
    title_display = title[:59]
    
    print(f"{title_display:<60} {extracted_display:<15} {status:<10}")

print("\n" + "="*70)
