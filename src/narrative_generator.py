"""
Narrative Generator Module - Enhanced
Generates formatted output with all enhancements
"""

from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from collections import Counter
from config import Config
from utils import percentage


class NarrativeGenerator:
    """Generates professional formatted narratives"""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Config.OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def generate_all_formats(
        self,
        session_data: Dict,
        analysis: Dict,
        narratives: Dict,
        quality_data: Optional[Dict] = None,
        temporal_data: Optional[Dict] = None,
        categorized_commits: Optional[List[Dict]] = None
    ) -> Dict[str, Path]:
        """Generate all output formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = {}

        for format_type, narrative in narratives.items():
            filename = f"devflow_{format_type}_{timestamp}.md"
            filepath = self.output_dir / filename

            content = self._format_document(
                format_type, session_data, analysis, narrative,
                quality_data, temporal_data, categorized_commits
            )

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            output_files[format_type] = filepath

            # Create latest link
            latest = self.output_dir / f"devflow_{format_type}_latest.md"
            if latest.exists():
                latest.unlink()
            try:
                latest.symlink_to(filepath.name)
            except (OSError, NotImplementedError):
                pass

        return output_files

    def _format_document(
        self, format_type: str, session_data: Dict, analysis: Dict,
        narrative: str, quality_data: Optional[Dict],
        temporal_data: Optional[Dict], categorized_commits: Optional[List[Dict]]
    ) -> str:
        """Create formatted markdown document"""

        doc = self._create_header(format_type, session_data)
        doc += f"\n##  {format_type.title()} Report\n\n{narrative}\n\n---\n\n"

        if categorized_commits:
            doc += self._create_category_breakdown(categorized_commits)

        if quality_data:
            doc += self._create_quality_section(quality_data)

        if temporal_data:
            doc += self._create_temporal_section(temporal_data)

        doc += self._create_analysis_section(analysis)
        doc += self._create_commit_details(session_data)
        doc += self._create_footer()

        return doc

    def _create_header(self, format_type: str, session_data: Dict) -> str:
        """Create document header"""
        start = session_data.get('start_time')
        end = session_data.get('end_time')

        return f"""# DevFlow Chronicle - {format_type.title()} Report

**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

---

##  Session Overview

| Metric | Value |
|--------|-------|
| **Duration** | {session_data.get('duration_formatted', 'N/A')} |
| **Time Period** | {start.strftime('%b %d, %I:%M %p') if start else 'N/A'} to {end.strftime('%b %d, %I:%M %p') if end else 'N/A'} |
| **Commits** | {session_data.get('commit_count', 0)} |
| **Files Changed** | {session_data.get('total_files_changed', 0)} |
| **Lines Added** | +{session_data.get('total_insertions', 0):,} |
| **Lines Removed** | -{session_data.get('total_deletions', 0):,} |
| **Net Change** | {session_data.get('total_insertions', 0) - session_data.get('total_deletions', 0):+,} |

---
"""

    def _create_category_breakdown(self, commits: List[Dict]) -> str:
        """Create category breakdown section"""
        categories = [c.get('category', 'unknown') for c in commits]
        counts = Counter(categories)
        total = len(commits)

        emoji_map = {
            'feature': '', 'bugfix': '', 'refactor': '',
            'docs': '', 'test': '', 'chore': '', 'style': ''
        }

        section = "##  Work Breakdown\n\n| Category | Commits | % | Lines |\n|----------|---------|---|-------|\n"

        for cat, count in counts.most_common():
            pct = percentage(count, total)
            cat_commits = [c for c in commits if c.get('category') == cat]
            lines_add = sum(c.get('insertions', 0) for c in cat_commits)
            lines_del = sum(c.get('deletions', 0) for c in cat_commits)

            emoji = emoji_map.get(cat, '')
            section += f"| {emoji} {cat.title()} | {count} | {pct:.0f}% | +{lines_add}/-{lines_del} |\n"

        return section + "\n---\n\n"

    def _create_quality_section(self, quality_data: Dict) -> str:
        """Create quality analysis section"""
        avg = quality_data.get('average_score', 0)

        section = f"""##  Quality Analysis

**Average Score:** {avg:.2f}/1.00

| Quality Level | Count |
|---------------|-------|
| High (>=0.8) | {quality_data.get('high_quality', 0)} commits |
| Medium (0.6-0.8) | {quality_data.get('medium_quality', 0)} commits |
| Needs Work (<0.6) | {quality_data.get('low_quality', 0)} commits |

---

"""
        return section

    def _create_temporal_section(self, temporal_data: Dict) -> str:
        """Create temporal patterns section"""
        section = f"""##  Productivity Patterns

**Peak Productivity:** {temporal_data.get('peak_day', 'N/A')} at {temporal_data.get('peak_hour', 0)}:00

**Time Distribution:**
-  Morning (6am-12pm): {temporal_data.get('morning_commits', 0)} commits
-  Afternoon (12pm-6pm): {temporal_data.get('afternoon_commits', 0)} commits
-  Evening (6pm-12am): {temporal_data.get('evening_commits', 0)} commits
-  Night (12am-6am): {temporal_data.get('night_commits', 0)} commits

**Productivity Rate:** {temporal_data.get('productivity_rate', 0):.1f} commits/day across {temporal_data.get('active_days', 0)} active days

---

"""
        return section

    def _create_analysis_section(self, analysis: Dict) -> str:
        """Create AI analysis section"""
        section = "##  AI Analysis\n\n"

        if analysis.get('work_types'):
            section += "**Work Types:**\n"
            for wt in analysis['work_types']:
                section += f"- {wt}\n"
            section += "\n"

        if analysis.get('focus_areas'):
            section += "**Focus Areas:**\n"
            for area in analysis['focus_areas']:
                section += f"- {area}\n"
            section += "\n"

        if analysis.get('technical_insights'):
            section += "**Technical Insights:**\n"
            for insight in analysis['technical_insights']:
                section += f"- {insight}\n"
            section += "\n"

        return section + "---\n\n"

    def _create_commit_details(self, session_data: Dict) -> str:
        """Create commit details section"""
        commits = session_data.get('commits', [])

        section = f"##  Commit Details\n\n"

        for commit in commits[:10]:
            section += f"### `{commit['hash']}` {commit['message'][:60]}\n"
            section += f"*{commit['timestamp'].strftime('%b %d, %I:%M %p')}* | "
            section += f"{commit['files_changed']} files | "
            section += f"+{commit['insertions']}/-{commit['deletions']}\n\n"

        if len(commits) > 10:
            section += f"*...and {len(commits) - 10} more commits*\n\n"

        return section

    def _create_footer(self) -> str:
        """Create document footer"""
        return """---

*Generated by **DevFlow Chronicle** - Your AI Development Companion*

 **Powered by Claude AI** |  **Containerized & Production-Ready**
"""

    def print_summary(self, output_files: Dict[str, Path]):
        """Print summary of generated files"""
        print("\n DevFlow Chronicle Reports Generated!\n")
        print("=" * 60)

        for fmt, path in output_files.items():
            size = path.stat().st_size
            print(f" {fmt.upper():12} -> {path}")
            print(f"   Size: {size:,} bytes\n")

        print("=" * 60)
