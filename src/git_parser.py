"""
Git Parser Module
Extracts commit history, metadata, and temporal patterns
Enhanced with temporal analysis for productivity insights
"""

from git import Repo
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import os


class GitParser:
    """
    Parses git repositories with advanced analysis capabilities
    Follows single responsibility principle with focused methods
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the Git Parser
        
        Args:
            repo_path: Path to the git repository
            
        Raises:
            ValueError: If path doesn't exist or isn't a git repo
        """
        if not os.path.exists(repo_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        try:
            self.repo = Repo(repo_path)
            self.repo_path = repo_path
        except Exception as e:
            raise ValueError(f"Invalid git repository: {e}")
    
    def get_recent_commits(self, limit: int = 20, branch: Optional[str] = None) -> List[Dict]:
        """
        Retrieve recent commits with comprehensive metadata
        
        Args:
            limit: Maximum number of commits to retrieve
            branch: Specific branch to analyze (None for current)
            
        Returns:
            List of commit dictionaries with metadata
        """
        commits = []
        
        try:
            commit_iter = self.repo.iter_commits(branch, max_count=limit)
            
            for commit in commit_iter:
                commit_data = {
                    'hash': commit.hexsha[:7],
                    'full_hash': commit.hexsha,
                    'message': commit.message.strip(),
                    'author': commit.author.name,
                    'author_email': commit.author.email,
                    'timestamp': datetime.fromtimestamp(commit.committed_date),
                    'files_changed': len(commit.stats.files),
                    'insertions': commit.stats.total['insertions'],
                    'deletions': commit.stats.total['deletions'],
                    'files': list(commit.stats.files.keys()),
                    'branches': [ref.name for ref in self.repo.refs if commit in ref.commit.iter_items(self.repo, ref.commit)]
                }
                commits.append(commit_data)
                
        except Exception as e:
            print(f"Warning: Error retrieving commits: {e}")
        
        return commits
    
    def group_into_sessions(self, commits: List[Dict], gap_hours: int = 3) -> List[List[Dict]]:
        """
        Group commits into work sessions based on time gaps
        
        Args:
            commits: List of commit dictionaries
            gap_hours: Hours gap to consider as separate session
            
        Returns:
            List of sessions (each session is a list of commits)
        """
        if not commits:
            return []
        
        # Sort by timestamp (oldest first for session building)
        sorted_commits = sorted(commits, key=lambda x: x['timestamp'])
        
        sessions = []
        current_session = [sorted_commits[0]]
        
        for i in range(1, len(sorted_commits)):
            time_gap = sorted_commits[i]['timestamp'] - current_session[-1]['timestamp']
            
            if time_gap > timedelta(hours=gap_hours):
                # Start new session
                sessions.append(current_session)
                current_session = [sorted_commits[i]]
            else:
                # Continue current session
                current_session.append(sorted_commits[i])
        
        # Add final session
        sessions.append(current_session)
        
        # Reverse to get most recent first
        return sessions[::-1]
    
    def get_session_summary(self, session: List[Dict]) -> Dict:
        """
        Create comprehensive summary statistics for a session
        
        Args:
            session: List of commits in the session
            
        Returns:
            Dictionary with session statistics
        """
        if not session:
            return {}
        
        # Sort session by time
        sorted_session = sorted(session, key=lambda x: x['timestamp'])
        
        duration = sorted_session[-1]['timestamp'] - sorted_session[0]['timestamp']
        
        # Collect all unique files
        all_files = set()
        for commit in session:
            all_files.update(commit['files'])
        
        return {
            'start_time': sorted_session[0]['timestamp'],
            'end_time': sorted_session[-1]['timestamp'],
            'duration': duration,
            'duration_formatted': self._format_duration(duration),
            'commit_count': len(session),
            'total_files_changed': len(all_files),
            'total_insertions': sum(c['insertions'] for c in session),
            'total_deletions': sum(c['deletions'] for c in session),
            'commits': session,
            'unique_files': list(all_files),
            'authors': list(set(c['author'] for c in session))
        }
    
    def analyze_temporal_patterns(self, commits: List[Dict]) -> Dict:
        """
        Analyze when commits happen for productivity insights
        
        Args:
            commits: List of commit dictionaries
            
        Returns:
            Temporal pattern analysis
        """
        if not commits:
            return {}
        
        hours = defaultdict(int)
        days = defaultdict(int)
        months = defaultdict(int)
        
        for commit in commits:
            timestamp = commit['timestamp']
            hours[timestamp.hour] += 1
            days[timestamp.strftime('%A')] += 1
            months[timestamp.strftime('%B %Y')] += 1
        
        # Find peaks
        peak_hour = max(hours.items(), key=lambda x: x[1])[0] if hours else 0
        peak_day = max(days.items(), key=lambda x: x[1])[0] if days else "Unknown"
        
        # Categorize by time of day
        morning = sum(v for h, v in hours.items() if 6 <= h < 12)
        afternoon = sum(v for h, v in hours.items() if 12 <= h < 18)
        evening = sum(v for h, v in hours.items() if 18 <= h < 24)
        night = sum(v for h, v in hours.items() if h < 6)
        
        # Calculate productivity score (commits per active day)
        active_days = len(set(c['timestamp'].date() for c in commits))
        productivity_rate = len(commits) / active_days if active_days > 0 else 0
        
        return {
            'by_hour': dict(hours),
            'by_day': dict(days),
            'by_month': dict(months),
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'morning_commits': morning,
            'afternoon_commits': afternoon,
            'evening_commits': evening,
            'night_commits': night,
            'active_days': active_days,
            'productivity_rate': round(productivity_rate, 2),
            'total_commits': len(commits)
        }
    
    def get_file_change_patterns(self, commits: List[Dict]) -> Dict:
        """
        Analyze which files/directories are changed most frequently
        
        Args:
            commits: List of commit dictionaries
            
        Returns:
            File change pattern analysis
        """
        file_changes = defaultdict(int)
        directory_changes = defaultdict(int)
        
        for commit in commits:
            for file in commit['files']:
                file_changes[file] += 1
                
                # Extract directory
                if '/' in file:
                    directory = '/'.join(file.split('/')[:-1])
                    directory_changes[directory] += 1
        
        # Get top files and directories
        top_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:10]
        top_dirs = sorted(directory_changes.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'top_files': top_files,
            'top_directories': top_dirs,
            'total_unique_files': len(file_changes),
            'total_directories': len(directory_changes)
        }
    
    def get_author_stats(self, commits: List[Dict]) -> Dict:
        """
        Get statistics by author (for team analysis)
        
        Args:
            commits: List of commit dictionaries
            
        Returns:
            Author statistics
        """
        author_commits = defaultdict(list)
        
        for commit in commits:
            author_commits[commit['author']].append(commit)
        
        author_stats = {}
        for author, author_commit_list in author_commits.items():
            author_stats[author] = {
                'commits': len(author_commit_list),
                'files_changed': sum(c['files_changed'] for c in author_commit_list),
                'insertions': sum(c['insertions'] for c in author_commit_list),
                'deletions': sum(c['deletions'] for c in author_commit_list)
            }
        
        return author_stats
    
    @staticmethod
    def _format_duration(td: timedelta) -> str:
        """Format timedelta as human-readable string"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        return " ".join(parts) if parts else "Less than a minute"


def test_parser():
    """Test the git parser on current directory"""
    try:
        parser = GitParser(".")
        commits = parser.get_recent_commits(10)
        print(f"[OK] Found {len(commits)} commits")
        
        if commits:
            print("\nRecent commits:")
            for commit in commits[:3]:
                print(f"  {commit['hash']}: {commit['message'][:50]}")
            
            sessions = parser.group_into_sessions(commits)
            print(f"\n[OK] Grouped into {len(sessions)} sessions")
            
            temporal = parser.analyze_temporal_patterns(commits)
            print(f"\n[OK] Peak productivity: {temporal['peak_day']} at {temporal['peak_hour']}:00")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")


if __name__ == "__main__":
    test_parser()
