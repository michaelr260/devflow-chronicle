"""
Multi-Repository Analyzer
Compare work patterns across multiple repositories
"""

from git_parser import GitParser
from claude_analyzer import ClaudeAnalyzer
from typing import List, Dict
import os


class MultiRepoAnalyzer:
    """Analyzes patterns across multiple repositories"""

    def __init__(self, repo_paths: List[str]):
        self.repo_paths = repo_paths
        self.analyzer = ClaudeAnalyzer()

    def analyze_all_repos(self, commits_per_repo: int = 20) -> Dict:
        """Analyze all repositories and aggregate"""
        repo_analyses = []

        for repo_path in self.repo_paths:
            try:
                print(f" Analyzing {os.path.basename(repo_path)}...")

                parser = GitParser(repo_path)
                commits = parser.get_recent_commits(commits_per_repo)

                if not commits:
                    continue

                analysis = self.analyzer.analyze_commits(commits)

                repo_analyses.append({
                    'path': repo_path,
                    'name': os.path.basename(repo_path),
                    'commits': len(commits),
                    'analysis': analysis
                })

            except Exception as e:
                print(f"     Skipped {repo_path}: {e}")

        return self._generate_comparison(repo_analyses)

    def _generate_comparison(self, repo_analyses: List[Dict]) -> Dict:
        """Generate cross-repository insights using Claude"""
        summary = "\n\n".join([
            f"**{r['name']}**\n"
            f"Commits: {r['commits']}\n"
            f"Focus: {', '.join(r['analysis'].get('focus_areas', []))}\n"
            f"Types: {', '.join(r['analysis'].get('work_types', []))}"
            for r in repo_analyses
        ])

        prompt = f"""Analyze work across these repositories:

{summary}

Provide JSON:
{{
    "main_focus_project": "project name",
    "common_themes": ["theme1", "theme2"],
    "work_balance": "description of balance",
    "recommendations": ["rec1", "rec2"]
}}
"""

        response = self.analyzer._call_claude(prompt, 1500)

        from utils import extract_json_from_text
        comparison = extract_json_from_text(response)
        comparison['repositories'] = repo_analyses

        return comparison

    def generate_dashboard(self, comparison: Dict) -> str:
        """Generate multi-repo dashboard markdown"""
        repos = comparison.get('repositories', [])

        dashboard = """#  Multi-Repository Dashboard

## Overview

"""

        total_commits = sum(r['commits'] for r in repos)

        dashboard += f"**Total Repositories:** {len(repos)}\n"
        dashboard += f"**Total Commits Analyzed:** {total_commits}\n\n"

        dashboard += "## Repository Breakdown\n\n"
        dashboard += "| Repository | Commits | % of Total |\n"
        dashboard += "|------------|---------|------------|\n"

        for repo in repos:
            pct = (repo['commits'] / total_commits * 100) if total_commits > 0 else 0
            dashboard += f"| {repo['name']} | {repo['commits']} | {pct:.1f}% |\n"

        dashboard += f"\n**Main Focus:** {comparison.get('main_focus_project', 'N/A')}\n\n"

        if comparison.get('common_themes'):
            dashboard += "## Common Themes\n\n"
            for theme in comparison['common_themes']:
                dashboard += f"- {theme}\n"

        if comparison.get('recommendations'):
            dashboard += "\n## Recommendations\n\n"
            for rec in comparison['recommendations']:
                dashboard += f"- {rec}\n"

        return dashboard
