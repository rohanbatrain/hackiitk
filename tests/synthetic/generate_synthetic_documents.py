#!/usr/bin/env python3
"""
Generate synthetic test documents for comprehensive testing.

This script creates 115+ synthetic documents covering:
- Stress testing (20 documents, 1-100 pages)
- Extreme structures (10 documents)
- Multilingual (15 documents, 10+ languages)
- Intentional gaps (50 documents)
- Performance profiling (20 documents)
"""

import sys
from pathlib import Path

# Add parent directory to path to import TestDataGenerator
sys.path.insert(0, str(Path(__file__).parent.parent / "extreme"))

from data_generator import TestDataGenerator, DocumentSpec
import logging


def generate_stress_testing_documents(generator: TestDataGenerator, output_dir: Path):
    """Generate stress testing documents (1-100 pages)."""
    print("\nGenerating stress testing documents...")
    
    page_counts = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    for pages in page_counts:
        spec = DocumentSpec(
            size_pages=pages,
            words_per_page=500,
            sections_per_page=3,
            coverage_percentage=0.5,
            include_csf_keywords=True,
            structure_type="normal",
            language="english"
        )
        
        document = generator.generate_policy_document(spec)
        
        # Pad filename with zeros for sorting
        filename = f"stress_{pages:03d}_{pages}pages.md"
        filepath = output_dir / filename
        filepath.write_text(document)
        
        print(f"  Created: {filename} ({pages} pages, ~{pages * 500} words)")


def generate_extreme_structure_documents(generator: TestDataGenerator, output_dir: Path):
    """Generate extreme structure documents."""
    print("\nGenerating extreme structure documents...")
    
    structures = [
        ("no_headings", "No headings"),
        ("deep_nesting", "Deep nesting (100+ levels)"),
        ("inconsistent_hierarchy", "Inconsistent hierarchy"),
        ("only_tables", "Only tables"),
        ("many_headings", "Many headings (1000+)"),
        ("many_sections", "Many sections (1000+)")
    ]
    
    for i, (structure_type, description) in enumerate(structures, start=1):
        document = generator.generate_extreme_structure(structure_type)
        
        filename = f"structure_{i:03d}_{structure_type}.md"
        filepath = output_dir / filename
        filepath.write_text(document)
        
        print(f"  Created: {filename} ({description})")


def generate_multilingual_documents(generator: TestDataGenerator, output_dir: Path):
    """Generate multilingual documents (10+ languages)."""
    print("\nGenerating multilingual documents...")
    
    language_sets = [
        (["chinese"], "Chinese"),
        (["arabic"], "Arabic (RTL)"),
        (["cyrillic"], "Cyrillic (Russian)"),
        (["emoji"], "Emoji"),
        (["greek"], "Greek (mathematical symbols)"),
        (["chinese", "english"], "Chinese + English"),
        (["arabic", "english"], "Arabic + English"),
        (["cyrillic", "english"], "Cyrillic + English"),
        (["emoji", "english"], "Emoji + English"),
        (["greek", "english"], "Greek + English"),
        (["chinese", "arabic"], "Chinese + Arabic"),
        (["chinese", "arabic", "cyrillic"], "Chinese + Arabic + Cyrillic"),
        (["chinese", "arabic", "cyrillic", "emoji"], "4 languages"),
        (["chinese", "arabic", "cyrillic", "emoji", "greek"], "5 languages"),
        (["chinese", "arabic", "cyrillic", "emoji", "greek", "english"], "6 languages (mixed)")
    ]
    
    for i, (languages, description) in enumerate(language_sets, start=1):
        document = generator.generate_multilingual_document(languages)
        
        filename = f"multilingual_{i:03d}_{'_'.join(languages[:2])}.md"
        filepath = output_dir / filename
        filepath.write_text(document)
        
        print(f"  Created: {filename} ({description})")


def generate_intentional_gap_documents(generator: TestDataGenerator, output_dir: Path):
    """Generate documents with intentional gaps."""
    print("\nGenerating intentional gap documents...")
    
    # All CSF subcategories
    all_subcategories = generator.CSF_SUBCATEGORIES
    
    # Generate documents with varying gap counts
    gap_counts = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 49]
    
    for gap_count in gap_counts:
        # Select random subcategories to be gaps
        import random
        random.seed(gap_count)  # Deterministic for reproducibility
        gap_subcategories = random.sample(all_subcategories, gap_count)
        
        document = generator.generate_gap_policy(gap_subcategories)
        
        filename = f"gap_{gap_count:03d}_gaps.md"
        filepath = output_dir / filename
        filepath.write_text(document)
        
        coverage_pct = ((len(all_subcategories) - gap_count) / len(all_subcategories)) * 100
        print(f"  Created: {filename} ({gap_count} gaps, {coverage_pct:.0f}% coverage)")
    
    # Generate specific gap patterns
    gap_patterns = [
        (["ID.AM-1", "ID.AM-2", "ID.AM-3"], "ID.AM gaps only"),
        (["PR.AC-1", "PR.AC-2", "PR.AC-3"], "PR.AC gaps only"),
        (["ID.RA-1", "ID.RA-2", "ID.RA-3"], "ID.RA gaps only"),
        ([f"ID.{x}" for x in ["AM-1", "BE-1", "GV-1", "RA-1", "RM-1"]], "One from each ID function"),
        ([f"PR.{x}" for x in ["AC-1", "AT-1", "DS-1", "IP-1", "MA-1", "PT-1"]], "One from each PR function")
    ]
    
    for i, (gap_list, description) in enumerate(gap_patterns, start=len(gap_counts) + 1):
        document = generator.generate_gap_policy(gap_list)
        
        filename = f"gap_pattern_{i:03d}_{description.replace(' ', '_')[:30]}.md"
        filepath = output_dir / filename
        filepath.write_text(document)
        
        print(f"  Created: {filename} ({description})")


def generate_performance_profiling_documents(generator: TestDataGenerator, output_dir: Path):
    """Generate documents optimized for performance profiling."""
    print("\nGenerating performance profiling documents...")
    
    # Baseline documents
    specs = [
        (DocumentSpec(size_pages=10, words_per_page=500, sections_per_page=3, coverage_percentage=0.5), 
         "baseline_10pages_50pct"),
        (DocumentSpec(size_pages=10, words_per_page=500, sections_per_page=10, coverage_percentage=0.5), 
         "many_sections_10pages"),
        (DocumentSpec(size_pages=10, words_per_page=2000, sections_per_page=3, coverage_percentage=0.5), 
         "long_sections_10pages"),
        (DocumentSpec(size_pages=50, words_per_page=500, sections_per_page=3, coverage_percentage=0.5), 
         "baseline_50pages_50pct"),
        (DocumentSpec(size_pages=100, words_per_page=500, sections_per_page=3, coverage_percentage=0.5), 
         "baseline_100pages_50pct"),
        (DocumentSpec(size_pages=10, words_per_page=500, sections_per_page=3, coverage_percentage=0.0), 
         "zero_coverage_10pages"),
        (DocumentSpec(size_pages=10, words_per_page=500, sections_per_page=3, coverage_percentage=1.0), 
         "full_coverage_10pages"),
        (DocumentSpec(size_pages=10, words_per_page=500, sections_per_page=3, coverage_percentage=0.25), 
         "low_coverage_10pages"),
        (DocumentSpec(size_pages=10, words_per_page=500, sections_per_page=3, coverage_percentage=0.75), 
         "high_coverage_10pages"),
        (DocumentSpec(size_pages=20, words_per_page=500, sections_per_page=5, coverage_percentage=0.5), 
         "medium_20pages_50pct")
    ]
    
    for i, (spec, description) in enumerate(specs, start=1):
        document = generator.generate_policy_document(spec)
        
        filename = f"perf_{i:03d}_{description}.md"
        filepath = output_dir / filename
        filepath.write_text(document)
        
        print(f"  Created: {filename} ({spec.size_pages} pages, {spec.coverage_percentage*100:.0f}% coverage)")


def generate_boundary_documents(generator: TestDataGenerator, output_dir: Path):
    """Generate documents for boundary testing."""
    print("\nGenerating boundary test documents...")
    
    # Documents with specific characteristics for boundary testing
    boundary_specs = [
        (DocumentSpec(size_pages=1, words_per_page=100, sections_per_page=1, coverage_percentage=0.5), 
         "minimum_viable_1page"),
        (DocumentSpec(size_pages=1, words_per_page=10, sections_per_page=1, coverage_percentage=0.0), 
         "tiny_10words"),
        (DocumentSpec(size_pages=1, words_per_page=1, sections_per_page=1, coverage_percentage=0.0), 
         "single_word"),
        (DocumentSpec(size_pages=100, words_per_page=5000, sections_per_page=10, coverage_percentage=1.0), 
         "maximum_100pages_full"),
        (DocumentSpec(size_pages=50, words_per_page=1000, sections_per_page=1, coverage_percentage=0.5), 
         "few_sections_50pages")
    ]
    
    for i, (spec, description) in enumerate(boundary_specs, start=1):
        document = generator.generate_policy_document(spec)
        
        filename = f"boundary_{i:03d}_{description}.md"
        filepath = output_dir / filename
        filepath.write_text(document)
        
        total_words = spec.size_pages * spec.words_per_page
        print(f"  Created: {filename} ({spec.size_pages} pages, ~{total_words} words)")


def main():
    """Generate all synthetic test documents."""
    # Set up output directory
    output_dir = Path(__file__).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Suppress info logs from generator
    
    # Initialize generator
    generator = TestDataGenerator()
    
    print("=" * 80)
    print("Generating Synthetic Test Documents")
    print("=" * 80)
    
    # Generate all document types
    generate_stress_testing_documents(generator, output_dir)
    generate_extreme_structure_documents(generator, output_dir)
    generate_multilingual_documents(generator, output_dir)
    generate_intentional_gap_documents(generator, output_dir)
    generate_performance_profiling_documents(generator, output_dir)
    generate_boundary_documents(generator, output_dir)
    
    # Count generated files
    generated_files = list(output_dir.glob("*.md"))
    
    print("\n" + "=" * 80)
    print(f"Generation Complete!")
    print("=" * 80)
    print(f"Total documents generated: {len(generated_files)}")
    print(f"Output directory: {output_dir}")
    
    # Create summary file
    summary = {
        "total_documents": len(generated_files),
        "categories": {
            "stress_testing": len(list(output_dir.glob("stress_*.md"))),
            "extreme_structure": len(list(output_dir.glob("structure_*.md"))),
            "multilingual": len(list(output_dir.glob("multilingual_*.md"))),
            "intentional_gaps": len(list(output_dir.glob("gap_*.md"))),
            "performance_profiling": len(list(output_dir.glob("perf_*.md"))),
            "boundary_testing": len(list(output_dir.glob("boundary_*.md")))
        },
        "files": sorted([f.name for f in generated_files])
    }
    
    import json
    summary_file = output_dir / "documents_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2))
    print(f"\nSummary saved to: {summary_file}")
    
    # Print category breakdown
    print("\nCategory Breakdown:")
    for category, count in summary["categories"].items():
        print(f"  {category.replace('_', ' ').title()}: {count} documents")


if __name__ == "__main__":
    main()
