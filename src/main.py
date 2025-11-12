#!/usr/bin/env python3
"""
DevFlow Chronicle - Main Application
Complete implementation with all 12 enhancements
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from config import Config
from git_parser import GitParser
from claude_analyzer import ClaudeAnalyzer
from narrative_generator import NarrativeGenerator
from quality_scorer import QualityScorer
from cache_manager import CacheManager
from multi_repo_analyzer import MultiRepoAnalyzer

# Optional imports
try:
    from commit_search import CommitSearchEngine
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='DevFlow Chronicle - AI-powered development workflow analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Analyze current directory
  %(prog)s /path/to/repo            # Analyze specific repo
  %(prog)s -n 50 -f standup weekly  # 50 commits, specific formats
  %(prog)s --preset daily           # Use daily preset
  %(prog)s --multi repo1 repo2      # Multi-repo analysis
  %(prog)s --interactive            # Interactive Q&A mode
        """
    )

    parser.add_argument(
        'repo_path',
        nargs='?',
        default='.',
        help='Path to git repository (default: current directory)'
    )

    parser.add_argument(
        '-n', '--num-commits',
        type=int,
        default=Config.DEFAULT_COMMIT_LIMIT,
        help=f'Number of commits to analyze (default: {Config.DEFAULT_COMMIT_LIMIT})'
    )

    parser.add_argument(
        '-f', '--formats',
        nargs='+',
        choices=Config.OUTPUT_FORMATS,
        default=Config.OUTPUT_FORMATS,
        help='Output formats to generate'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default=str(Config.OUTPUT_DIR),
        help='Output directory for reports'
    )

    parser.add_argument(
        '--preset',
        help='Use configuration preset (daily, weekly, review)'
    )

    parser.add_argument(
        '--multi',
        nargs='+',
        metavar='REPO',
        help='Multi-repository analysis mode'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Enter interactive Q&A mode after analysis'
    )

    parser.add_argument(
        '--search',
        help='Search for similar commits (requires vector search)'
    )

    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear API response cache'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching for this run'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show cache statistics'
    )

    return parser.parse_args()


def main():
    """Main application entry point"""
    args = parse_arguments()

    # Apply preset if specified
    if args.preset:
        Config.apply_preset(args.preset)

    # Handle cache operations
    cache = CacheManager()

    if args.clear_cache:
        cache.clear_all()
        return 0

    if args.stats:
        cache.print_stats()
        return 0

    # Print banner
    print("DevFlow Chronicle - AI Development Workflow Analyzer")
    print("=" * 70)

    # Multi-repo mode
    if args.multi:
        return handle_multi_repo(args)

    # Single repo mode
    return handle_single_repo(args, cache)


def handle_single_repo(args, cache):
    """Handle single repository analysis"""

    # Step 1: Parse Git Repository
    print(f"\n[STEP 1/7] Parsing repository '{args.repo_path}'...")
    try:
        parser = GitParser(args.repo_path)
        commits = parser.get_recent_commits(args.num_commits)
        print(f"   [OK] Found {len(commits)} commits")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return 1

    if not commits:
        print("\n   [WARNING] No commits found")
        return 1

    # Step 2: Group into sessions
    print(f"\n Step 2/7: Grouping commits into work sessions...")
    sessions = parser.group_into_sessions(commits, Config.SESSION_GAP_HOURS)
    print(f"   [OK] Identified {len(sessions)} work session(s)")

    if not sessions:
        print("\n     No sessions found")
        return 1

    recent_session = sessions[0]
    session_summary = parser.get_session_summary(recent_session)

    print(f"\n   Most Recent Session:")
    print(f"   * Duration: {session_summary['duration_formatted']}")
    print(f"   * Commits: {session_summary['commit_count']}")
    print(f"   * Files: {session_summary['total_files_changed']}")

    # Step 3: Initialize Claude Analyzer
    print(f"\n Step 3/7: Initializing AI analyzer...")
    try:
        analyzer = ClaudeAnalyzer(use_cache=not args.no_cache)
        print("   [OK] Claude analyzer ready")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return 1

    # Step 4: Comprehensive Analysis
    print(f"\n Step 4/7: Running comprehensive analysis...")

    # Basic analysis
    analysis = analyzer.analyze_commits(recent_session)
    print("   [OK] Basic analysis complete")

    # Style analysis
    style_profile = analyzer.analyze_writing_style(commits)
    print(f"   [OK] Style profile: {style_profile.get('tone', 'unknown')} tone")

    # Categorize commits
    categorized_commits = analyzer.categorize_commits(recent_session)
    print("   [OK] Commits categorized")

    # Quality scoring
    scorer = QualityScorer()
    scored_commits = scorer.score_commits(categorized_commits)
    quality_summary = scorer.get_summary_stats(scored_commits)
    print(f"   [OK] Quality scored (avg: {quality_summary.get('average_score', 0):.2f})")

    # Temporal analysis
    temporal_data = parser.analyze_temporal_patterns(commits)
    print(f"   [OK] Temporal patterns: peak on {temporal_data['peak_day']}")

    # Step 5: Vector search (if requested and available)
    if args.search and SEARCH_AVAILABLE:
        print(f"\n Step 5/7: Semantic search...")
        try:
            search_engine = CommitSearchEngine()
            search_engine.index_commits(commits)
            results = search_engine.search(args.search)

            print(f"   Results for '{args.search}':")
            for r in results[:3]:
                c = r['commit']
                print(f"   * [{c['hash']}] {c['message'][:50]} (similarity: {r['similarity']:.2f})")
        except Exception as e:
            print(f"     Search error: {e}")
    else:
        print(f"\n   Step 5/7: Skipped (search not requested)")

    # Step 6: Generate narratives
    print(f"\n Step 6/7: Generating narratives ({len(args.formats)} formats)...")
    narratives = {}

    for format_type in args.formats:
        try:
            narrative = analyzer.generate_narrative(
                session_summary,
                analysis,
                format_type,
                style_profile
            )
            narratives[format_type] = narrative
            print(f"   [OK] {format_type.title()} format")
        except Exception as e:
            print(f"   [ERROR] Error generating {format_type}: {e}")

    # Step 7: Save outputs
    print(f"\n Step 7/7: Saving reports...")
    try:
        generator = NarrativeGenerator(Path(args.output_dir))
        output_files = generator.generate_all_formats(
            session_summary,
            analysis,
            narratives,
            quality_summary,
            temporal_data,
            scored_commits
        )
        generator.print_summary(output_files)
    except Exception as e:
        print(f"   [ERROR] Error saving outputs: {e}")
        return 1

    # Cache statistics
    if not args.no_cache:
        stats = cache.get_stats()
        print(f"\n Cache: {stats['hits']} hits, {stats['misses']} misses ({stats['hit_rate']:.1f}% hit rate)")

    # Interactive mode
    if args.interactive:
        interactive_mode(commits, analysis, analyzer)

    print("\n Analysis complete!\n")
    return 0


def handle_multi_repo(args):
    """Handle multi-repository analysis"""
    print(f"\n Multi-Repository Analysis Mode")
    print(f"   Analyzing {len(args.multi)} repositories...\n")

    try:
        multi_analyzer = MultiRepoAnalyzer(args.multi)
        comparison = multi_analyzer.analyze_all_repos(args.num_commits)

        dashboard = multi_analyzer.generate_dashboard(comparison)

        # Save dashboard
        output_path = Path(args.output_dir) / f"multi_repo_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(output_path, 'w') as f:
            f.write(dashboard)

        print(f"\n Multi-repo dashboard saved: {output_path}\n")
        return 0

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return 1


def interactive_mode(commits, analysis, analyzer):
    """Interactive Q&A mode"""
    print("\n Interactive Mode - Ask questions about your work")
    print("   Type 'exit' to quit\n")

    import json
    context = f"Analysis: {json.dumps(analysis, indent=2)}\nCommits: {len(commits)}"

    while True:
        try:
            question = input("You: ").strip()

            if question.lower() in ['exit', 'quit', 'q']:
                break

            if not question:
                continue

            prompt = f"{context}\n\nQuestion: {question}\n\nAnswer concisely:"
            response = analyzer._call_claude(prompt, 800)

            print(f"\nClaude: {response}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\n Exiting interactive mode")


if __name__ == "__main__":
    sys.exit(main())
