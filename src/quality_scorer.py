"""
Quality Scorer Module
Analyzes commit quality and provides improvement suggestions
"""

from typing import List, Dict
from config import Config


class QualityScorer:
    """Scores commit quality based on multiple criteria"""

    def __init__(self):
        self.imperative_verbs = [
            'add', 'fix', 'update', 'remove', 'refactor', 'implement',
            'create', 'delete', 'modify', 'improve', 'optimize',
            'enhance', 'resolve', 'correct', 'adjust', 'integrate'
        ]

        self.generic_messages = [
            'update', 'fix stuff', 'changes', 'wip', 'work in progress',
            'misc', 'various', 'stuff', 'things', 'quick fix'
        ]

    def score_commits(self, commits: List[Dict]) -> List[Dict]:
        """Score all commits for quality"""
        scored_commits = []

        for commit in commits:
            score_details = self._score_single_commit(commit)
            commit_with_score = commit.copy()
            commit_with_score['quality_score'] = score_details
            scored_commits.append(commit_with_score)

        return scored_commits

    def _score_single_commit(self, commit: Dict) -> Dict:
        """Score a single commit"""
        message = commit['message']

        message_score = self._score_message_quality(message)
        size_score = self._score_size_appropriateness(commit)
        focus_score = self._score_focus(commit)

        overall = (message_score + size_score + focus_score) / 3

        if overall >= Config.QUALITY_THRESHOLD_HIGH:
            grade = 'A'
        elif overall >= Config.QUALITY_THRESHOLD_LOW:
            grade = 'B'
        else:
            grade = 'C'

        return {
            'message_quality': round(message_score, 2),
            'size_appropriateness': round(size_score, 2),
            'focus': round(focus_score, 2),
            'overall': round(overall, 2),
            'grade': grade,
            'suggestions': self._generate_suggestions(commit, message_score, size_score, focus_score)
        }

    def _score_message_quality(self, message: str) -> float:
        """Score commit message quality"""
        score = 0.5

        msg_length = len(message)
        if 10 < msg_length < 100:
            score += 0.15
        elif msg_length < 10:
            score -= 0.2
        elif msg_length > 150:
            score -= 0.1

        first_word = message.split()[0].lower() if message else ""
        if first_word in self.imperative_verbs:
            score += 0.20

        is_generic = any(generic in message.lower() for generic in self.generic_messages)
        if not is_generic:
            score += 0.15
        else:
            score -= 0.15

        if message and message[0].isupper():
            score += 0.05

        if not message.endswith('.'):
            score += 0.05

        return max(0.0, min(1.0, score))

    def _score_size_appropriateness(self, commit: Dict) -> float:
        """Score commit size appropriateness"""
        total_changes = commit.get('insertions', 0) + commit.get('deletions', 0)
        files_changed = commit.get('files_changed', 0)

        if total_changes < Config.SIZE_SMALL:
            size_score = 1.0
        elif total_changes < Config.SIZE_MEDIUM:
            size_score = 0.85
        elif total_changes < Config.SIZE_LARGE:
            size_score = 0.65
        else:
            size_score = 0.35

        if files_changed > 10:
            size_score *= 0.8
        elif files_changed > 20:
            size_score *= 0.6

        return size_score

    def _score_focus(self, commit: Dict) -> float:
        """Score whether commit is focused"""
        files = commit.get('files', [])

        if not files:
            return 0.5

        directories = set(f.split('/')[0] if '/' in f else '' for f in files)

        if len(directories) == 1:
            return 1.0
        elif len(directories) <= 3:
            return 0.75
        elif len(directories) <= 5:
            return 0.5
        else:
            return 0.3

    def _generate_suggestions(self, commit: Dict, msg_score: float,
                            size_score: float, focus_score: float) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        message = commit['message']

        if msg_score < 0.6:
            if len(message) < 10:
                suggestions.append("Add more detail to commit message")

            first_word = message.split()[0].lower() if message else ""
            if first_word not in self.imperative_verbs:
                suggestions.append("Start with imperative verb (add, fix, update, etc.)")

            if any(generic in message.lower() for generic in self.generic_messages):
                suggestions.append("Be more specific - avoid generic terms")

        if size_score < 0.6:
            total_changes = commit.get('insertions', 0) + commit.get('deletions', 0)
            if total_changes > Config.SIZE_LARGE:
                suggestions.append(f"Split into smaller commits (current: {total_changes} lines)")

        if focus_score < 0.6:
            files_changed = commit.get('files_changed', 0)
            if files_changed > 10:
                suggestions.append(f"Commit touches many files ({files_changed}) - consider splitting")

        return suggestions

    def generate_quality_report(self, scored_commits: List[Dict]) -> str:
        """Generate comprehensive quality report"""
        if not scored_commits:
            return "No commits to analyze."

        total = len(scored_commits)
        avg_score = sum(c['quality_score']['overall'] for c in scored_commits) / total

        grade_counts = {}
        for commit in scored_commits:
            grade = commit['quality_score']['grade']
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        low_quality = [
            c for c in scored_commits
            if c['quality_score']['overall'] < Config.QUALITY_THRESHOLD_LOW
        ]

        report = f"""
##  Commit Quality Report

**Overall Quality Score:** {avg_score:.2f}/1.00

**Grade Distribution:**
"""

        for grade in ['A', 'B', 'C']:
            count = grade_counts.get(grade, 0)
            percentage = (count / total * 100)
            bar = "#" * int(percentage / 5)
            report += f"- Grade {grade}: {count:2d} commits ({percentage:5.1f}%) {bar}\n"

        if low_quality:
            report += f"\n**Commits Needing Improvement:** {len(low_quality)}\n\n"

            for commit in low_quality[:5]:
                score = commit['quality_score']
                report += f"### `{commit['hash']}` - Grade {score['grade']} ({score['overall']:.2f})\n"
                report += f"**Message:** {commit['message'][:80]}\n"

                if score['suggestions']:
                    report += "**Suggestions:**\n"
                    for suggestion in score['suggestions']:
                        report += f"- {suggestion}\n"
                report += "\n"
        else:
            report += "\n **Excellent work! All commits meet quality standards.**\n"

        report += """
###  Best Practices

1. **Messages:** Start with imperative verb, be specific, keep under 72 chars
2. **Size:** Aim for < 200 lines per commit, one logical change
3. **Focus:** Group related files, avoid mixing unrelated changes
"""

        return report

    def get_summary_stats(self, scored_commits: List[Dict]) -> Dict:
        """Get summary statistics"""
        if not scored_commits:
            return {}

        total = len(scored_commits)

        return {
            'total_commits': total,
            'average_score': sum(c['quality_score']['overall'] for c in scored_commits) / total,
            'high_quality': len([c for c in scored_commits if c['quality_score']['overall'] >= Config.QUALITY_THRESHOLD_HIGH]),
            'medium_quality': len([c for c in scored_commits if Config.QUALITY_THRESHOLD_LOW <= c['quality_score']['overall'] < Config.QUALITY_THRESHOLD_HIGH]),
            'low_quality': len([c for c in scored_commits if c['quality_score']['overall'] < Config.QUALITY_THRESHOLD_LOW]),
            'needs_improvement': len([c for c in scored_commits if c['quality_score']['suggestions']])
        }
