"""
Claude Analyzer Module
Complete AI-powered analysis with all enhancements
Includes: style learning, categorization, quality scoring, temporal insights
"""

from anthropic import Anthropic
from typing import List, Dict, Optional
import json
from config import Config
from cache_manager import CacheManager
from utils import extract_json_from_text, safe_json_loads


class ClaudeAnalyzer:
    """
    Comprehensive Claude-powered analysis engine
    Implements all enhancement features
    """
    
    def __init__(self, use_cache: bool = True):
        """
        Initialize Claude client with caching
        
        Args:
            use_cache: Whether to use response caching
            
        Raises:
            ValueError: If API key not configured
        """
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL
        self.cache = CacheManager() if use_cache else None
    
    def _call_claude(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Call Claude API with caching
        
        Args:
            prompt: Prompt to send
            max_tokens: Maximum response tokens
            
        Returns:
            Claude's response text
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(prompt, self.model)
            if cached:
                return cached
        
        # Call API
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = message.content[0].text
            
            # Cache response
            if self.cache:
                self.cache.set(prompt, self.model, response)
            
            return response
            
        except Exception as e:
            raise Exception(f"Claude API error: {e}")
    
    def analyze_commits(self, commits: List[Dict]) -> Dict:
        """
        Comprehensive commit analysis
        
        Args:
            commits: List of commit dictionaries
            
        Returns:
            Analysis results from Claude
        """
        commit_summary = self._format_commits_for_analysis(commits)
        
        prompt = f"""Analyze these git commits and provide comprehensive insights:

{commit_summary}

Provide analysis as JSON with these keys:
- work_types: array of work types (feature, bugfix, refactor, docs, test, chore)
- focus_areas: array of main topics/components worked on
- patterns: array of observed patterns in commits or timing
- technical_insights: array of technical observations
- summary: brief overall summary (2-3 sentences)
- complexity_level: low/medium/high based on changes
- recommendations: array of suggestions for next steps

Respond ONLY with valid JSON.
"""
        
        response = self._call_claude(prompt)
        return extract_json_from_text(response)
    
    def analyze_writing_style(self, commits: List[Dict]) -> Dict:
        """
        Learn developer's personal writing style from commits
        
        Args:
            commits: List of commit dictionaries
            
        Returns:
            Style profile dictionary
        """
        messages = [c['message'] for c in commits[:30]]  # Sample recent commits
        
        prompt = f"""Analyze the writing style in these commit messages:

{chr(10).join(f"{i+1}. {msg}" for i, msg in enumerate(messages))}

Identify the author's personal style and return JSON:
{{
    "tone": "casual/professional/technical",
    "common_phrases": ["phrase1", "phrase2", "phrase3"],
    "structure_preference": "imperative/descriptive/mixed",
    "uses_emojis": true/false,
    "formality_level": 1-10,
    "unique_traits": ["trait1", "trait2"],
    "typical_length": "short/medium/long",
    "detail_level": "minimal/moderate/verbose"
}}

Respond ONLY with valid JSON.
"""
        
        response = self._call_claude(prompt, max_tokens=1000)
        return extract_json_from_text(response)
    
    def categorize_commits(self, commits: List[Dict]) -> List[Dict]:
        """
        Categorize each commit by type
        
        Args:
            commits: List of commit dictionaries
            
        Returns:
            Commits with added category information
        """
        # Batch process for efficiency
        commit_summaries = "\n".join([
            f"{i+1}. [{c['hash']}] {c['message'][:100]} "
            f"(files: {c['files_changed']}, +{c['insertions']}/-{c['deletions']})"
            for i, c in enumerate(commits)
        ])
        
        prompt = f"""Categorize each commit into ONE primary type:
- feature: New functionality
- bugfix: Fixing errors/bugs
- refactor: Code improvement without behavior change
- docs: Documentation changes
- test: Test additions/modifications
- chore: Build, config, dependencies, tooling
- style: Formatting, whitespace, linting

Commits:
{commit_summaries}

Return JSON array:
[
    {{"index": 1, "category": "feature", "confidence": 0.95, "reason": "adds new feature"}},
    ...
]

Respond ONLY with valid JSON array.
"""
        
        response = self._call_claude(prompt, max_tokens=2500)
        categorizations = extract_json_from_text(response)
        
        if isinstance(categorizations, list):
            # Apply categories to commits
            for cat in categorizations:
                idx = cat.get('index', 0) - 1
                if 0 <= idx < len(commits):
                    commits[idx]['category'] = cat.get('category', 'unknown')
                    commits[idx]['confidence'] = cat.get('confidence', 0.5)
                    commits[idx]['category_reason'] = cat.get('reason', '')
        
        return commits
    
    def generate_narrative(self, session_data: Dict, analysis: Dict, 
                          format_type: str, style_profile: Optional[Dict] = None) -> str:
        """
        Generate narrative with optional style matching
        
        Args:
            session_data: Session summary data
            analysis: Claude's analysis results
            format_type: Output format type
            style_profile: Optional personal style to match
            
        Returns:
            Generated narrative text
        """
        format_prompts = {
            "standup": """Generate a standup update in this format:

**Yesterday:**
[Specific accomplishments - be concrete]

**Today:**
[Planned work based on momentum]

**Blockers:**
[Any challenges or none]

Keep it concise, clear, and actionable.""",

            "technical": """Generate a detailed technical log:
- Document what was built/fixed/refactored with technical detail
- Include rationale for key decisions
- Note interesting challenges or solutions
- Use appropriate technical terminology
- Organize by theme or component

Make it thorough but well-structured.""",

            "weekly": """Generate a weekly digest:
- Executive summary of accomplishments
- Key metrics (commits, files, lines changed)
- Major themes and focus areas  
- Notable achievements and learnings
- Brief forward look

Professional tone, suitable for team sharing.""",

            "insights": """Generate productivity and pattern insights:
- Work pattern analysis (when, how, what)
- Effectiveness observations
- Technical growth areas
- Actionable improvement suggestions
- Balance and sustainability notes

Be constructive, specific, and growth-oriented."""
        }
        
        # Build style instructions if profile provided
        style_instructions = ""
        if style_profile:
            style_instructions = f"""
CRITICAL - Match the author's personal writing style:
- Tone: {style_profile.get('tone', 'professional')}
- Formality: {style_profile.get('formality_level', 5)}/10
- Structure: {style_profile.get('structure_preference', 'imperative')}
- Detail level: {style_profile.get('detail_level', 'moderate')}
- Common phrases to use naturally: {', '.join(style_profile.get('common_phrases', [])[:3])}

Write as if THEY wrote it, not a generic AI. Match their voice.
"""
        
        prompt = f"""{style_instructions}

Based on this development session:

**Session Duration:** {session_data.get('duration_formatted', 'N/A')}
**Commits:** {session_data.get('commit_count', 0)}
**Files Changed:** {session_data.get('total_files_changed', 0)}
**Lines:** +{session_data.get('total_insertions', 0)} -{session_data.get('total_deletions', 0)}

**AI Analysis:**
{json.dumps(analysis, indent=2)}

**Recent Commits:**
{chr(10).join([f"- {c.get('message', '')}" for c in session_data.get('commits', [])[:10]])}

{format_prompts.get(format_type, format_prompts['standup'])}
"""
        
        return self._call_claude(prompt, max_tokens=1500)
    
    def interpret_temporal_patterns(self, temporal_data: Dict) -> str:
        """
        Get insights on productivity patterns
        
        Args:
            temporal_data: Temporal pattern analysis
            
        Returns:
            Natural language insights
        """
        prompt = f"""Analyze these work timing patterns:

**Peak Productivity:**
- Best day: {temporal_data.get('peak_day', 'Unknown')}
- Best hour: {temporal_data.get('peak_hour', 0)}:00
- Active days: {temporal_data.get('active_days', 0)}
- Commits per day: {temporal_data.get('productivity_rate', 0)}

**Time Distribution:**
- Morning (6am-12pm): {temporal_data.get('morning_commits', 0)} commits
- Afternoon (12pm-6pm): {temporal_data.get('afternoon_commits', 0)} commits
- Evening (6pm-12am): {temporal_data.get('evening_commits', 0)} commits
- Night (12am-6am): {temporal_data.get('night_commits', 0)} commits

Provide insights on:
1. Energy and focus patterns
2. Work-life balance observations
3. Optimization opportunities
4. Schedule recommendations

Be specific, actionable, and respectful of different work styles.
"""
        
        return self._call_claude(prompt, max_tokens=1000)
    
    def generate_quality_insights(self, quality_summary: Dict) -> str:
        """
        Generate insights from quality analysis
        
        Args:
            quality_summary: Quality statistics summary
            
        Returns:
            Quality insights narrative
        """
        prompt = f"""Based on commit quality analysis:

**Overall Stats:**
- Total commits: {quality_summary.get('total_commits', 0)}
- Average score: {quality_summary.get('average_score', 0):.2f}/1.00
- High quality: {quality_summary.get('high_quality', 0)} commits
- Need improvement: {quality_summary.get('low_quality', 0)} commits

Provide:
1. Overall quality assessment
2. Specific strengths in commit practices
3. Top 2-3 areas for improvement
4. Practical tips for better commits

Be encouraging but honest. Focus on growth.
"""
        
        return self._call_claude(prompt, max_tokens=1000)
    
    @staticmethod
    def _format_commits_for_analysis(commits: List[Dict]) -> str:
        """Format commits for Claude analysis"""
        lines = []
        
        for i, commit in enumerate(commits[:25], 1):  # Limit for token efficiency
            timestamp = commit['timestamp'].strftime('%Y-%m-%d %H:%M')
            lines.append(
                f"{i}. [{timestamp}] {commit['hash']}: {commit['message']}\n"
                f"   Files: {commit['files_changed']}, "
                f"+{commit['insertions']}/-{commit['deletions']}"
            )
        
        return "\n".join(lines)


def test_analyzer():
    """Test Claude analyzer"""
    print("Testing Claude Analyzer...")
    
    analyzer = ClaudeAnalyzer()
    
    sample_commits = [
        {
            'hash': 'abc1234',
            'message': 'Add user authentication with JWT tokens',
            'timestamp': '2024-01-15 14:30',
            'files_changed': 3,
            'insertions': 145,
            'deletions': 12
        }
    ]
    
    analysis = analyzer.analyze_commits(sample_commits)
    print(f"[OK] Analysis: {json.dumps(analysis, indent=2)}")


if __name__ == "__main__":
    test_analyzer()
