"""
Git utilities and version control tools
"""

import subprocess
import os
import re
from typing import List, Dict, Optional
from datetime import datetime
from smolagents import tool


def run_git_command(args: List[str], cwd: str = None) -> Dict:
    """Run a git command and return results."""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'stdout': '', 'stderr': 'Command timed out', 'returncode': -1}
    except Exception as e:
        return {'success': False, 'stdout': '', 'stderr': str(e), 'returncode': -1}


@tool
def git_init(path: str = '.') -> Dict:
    """Initialize a git repository.

    Args:
        path: Path where the repository should be initialized.
    """
    return run_git_command(['init'], cwd=path)


@tool
def git_clone(url: str, path: str = None) -> Dict:
    """Clone a git repository.

    Args:
        url: The URL of the repository to clone.
        path: Optional local path to clone into.
    """
    args = ['clone', url]
    if path:
        args.append(path)
    return run_git_command(args)


@tool
def git_add(files: List[str], cwd: str = '.') -> Dict:
    """Add files to staging.

    Args:
        files: List of file paths to stage.
        cwd: Working directory (repository root).
    """
    return run_git_command(['add'] + files, cwd=cwd)


@tool
def git_add_all(cwd: str = '.') -> Dict:
    """Add all files to staging.

    Args:
        cwd: Working directory (repository root).
    """
    return run_git_command(['add', '.'], cwd=cwd)


@tool
def git_commit(message: str, cwd: str = '.') -> Dict:
    """Commit staged changes.

    Args:
        message: The commit message.
        cwd: Working directory (repository root).
    """
    return run_git_command(['commit', '-m', message], cwd=cwd)


@tool
def git_push(remote: str = 'origin', branch: str = None, cwd: str = '.') -> Dict:
    """Push changes to remote.

    Args:
        remote: Remote name (default 'origin').
        branch: Branch name to push (optional).
        cwd: Working directory (repository root).
    """
    args = ['push', remote]
    if branch:
        args.append(branch)
    return run_git_command(args, cwd=cwd)


@tool
def git_pull(remote: str = 'origin', branch: str = None, cwd: str = '.') -> Dict:
    """Pull changes from remote.

    Args:
        remote: Remote name (default 'origin').
        branch: Branch name to pull (optional).
        cwd: Working directory (repository root).
    """
    args = ['pull', remote]
    if branch:
        args.append(branch)
    return run_git_command(args, cwd=cwd)


@tool
def git_fetch(remote: str = 'origin', cwd: str = '.') -> Dict:
    """Fetch from remote.

    Args:
        remote: Remote name (default 'origin').
        cwd: Working directory (repository root).
    """
    return run_git_command(['fetch', remote], cwd=cwd)


@tool
def git_merge(branch: str, cwd: str = '.') -> Dict:
    """Merge a branch into current branch.

    Args:
        branch: Name of the branch to merge in.
        cwd: Working directory (repository root).
    """
    return run_git_command(['merge', branch], cwd=cwd)


@tool
def git_checkout(branch: str, cwd: str = '.') -> Dict:
    """Checkout a branch.

    Args:
        branch: Name of the branch to checkout.
        cwd: Working directory (repository root).
    """
    return run_git_command(['checkout', branch], cwd=cwd)


@tool
def git_checkout_new_branch(branch: str, cwd: str = '.') -> Dict:
    """Create and checkout a new branch.

    Args:
        branch: Name of the new branch to create and checkout.
        cwd: Working directory (repository root).
    """
    return run_git_command(['checkout', '-b', branch], cwd=cwd)


@tool
def git_create_branch(branch: str, from_branch: str = None, cwd: str = '.') -> Dict:
    """Create a new branch.

    Args:
        branch: Name of the new branch.
        from_branch: Base branch to create from (optional).
        cwd: Working directory (repository root).
    """
    args = ['branch', branch]
    if from_branch:
        args.append(from_branch)
    return run_git_command(args, cwd=cwd)


@tool
def git_delete_branch(branch: str, force: bool = False, cwd: str = '.') -> Dict:
    """Delete a branch.

    Args:
        branch: Name of the branch to delete.
        force: If True, force-delete even if unmerged.
        cwd: Working directory (repository root).
    """
    args = ['branch', '-d' if not force else '-D', branch]
    return run_git_command(args, cwd=cwd)


@tool
def git_list_branches(cwd: str = '.') -> List[str]:
    """List all branches.

    Args:
        cwd: Working directory (repository root).
    """
    result = run_git_command(['branch', '-a'], cwd=cwd)
    if result['success']:
        return [b.strip().lstrip('* ').lstrip() for b in result['stdout'].split('\n') if b.strip()]
    return []


@tool
def git_current_branch(cwd: str = '.') -> str:
    """Get current branch name.

    Args:
        cwd: Working directory (repository root).
    """
    result = run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=cwd)
    return result['stdout'] if result['success'] else 'unknown'


@tool
def git_status(cwd: str = '.') -> Dict:
    """Get git status.

    Args:
        cwd: Working directory (repository root).
    """
    return run_git_command(['status', '--short'], cwd=cwd)


@tool
def git_log(limit: int = 10, cwd: str = '.') -> List[Dict]:
    """Get commit log.

    Args:
        limit: Number of commits to retrieve.
        cwd: Working directory (repository root).
    """
    result = run_git_command([
        'log', f'-{limit}', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=iso'
    ], cwd=cwd)
    if not result['success']:
        return []

    commits = []
    for line in result['stdout'].split('\n'):
        if line:
            parts = line.split('|', 4)
            if len(parts) >= 5:
                commits.append({
                    'hash': parts[0],
                    'author': parts[1],
                    'email': parts[2],
                    'date': parts[3],
                    'message': parts[4]
                })
    return commits


@tool
def git_diff(file: str = None, cwd: str = '.') -> str:
    """Get diff of changes.

    Args:
        file: Optional specific file to diff.
        cwd: Working directory (repository root).
    """
    args = ['diff']
    if file:
        args.append(file)
    result = run_git_command(args, cwd=cwd)
    return result['stdout'] if result['success'] else ''


@tool
def git_show(commit_hash: str, cwd: str = '.') -> str:
    """Show commit details.

    Args:
        commit_hash: The commit hash to show.
        cwd: Working directory (repository root).
    """
    result = run_git_command(['show', commit_hash], cwd=cwd)
    return result['stdout'] if result['success'] else ''


@tool
def git_stash(message: str = None, cwd: str = '.') -> Dict:
    """Stash changes.

    Args:
        message: Optional stash message.
        cwd: Working directory (repository root).
    """
    args = ['stash', 'save'] if message else ['stash']
    if message:
        args.append(message)
    return run_git_command(args, cwd=cwd)


@tool
def git_stash_pop(cwd: str = '.') -> Dict:
    """Pop from stash.

    Args:
        cwd: Working directory (repository root).
    """
    return run_git_command(['stash', 'pop'], cwd=cwd)


@tool
def git_stash_list(cwd: str = '.') -> List[str]:
    """List stashes.

    Args:
        cwd: Working directory (repository root).
    """
    result = run_git_command(['stash', 'list'], cwd=cwd)
    if result['success']:
        return [s.strip() for s in result['stdout'].split('\n') if s.strip()]
    return []


@tool
def git_remote_list(cwd: str = '.') -> List[Dict]:
    """List remotes.

    Args:
        cwd: Working directory (repository root).
    """
    result = run_git_command(['remote', '-v'], cwd=cwd)
    if not result['success']:
        return []

    remotes = {}
    for line in result['stdout'].split('\n'):
        if line:
            parts = line.split()
            if len(parts) >= 3:
                name = parts[0]
                url = parts[1]
                direction = parts[2].strip('()')
                if name not in remotes:
                    remotes[name] = {'fetch': '', 'push': ''}
                remotes[name][direction] = url
    return [{'name': k, **v} for k, v in remotes.items()]


@tool
def git_remote_add(name: str, url: str, cwd: str = '.') -> Dict:
    """Add a remote.

    Args:
        name: Name for the new remote.
        url: URL of the remote repository.
        cwd: Working directory (repository root).
    """
    return run_git_command(['remote', 'add', name, url], cwd=cwd)


@tool
def git_remote_remove(name: str, cwd: str = '.') -> Dict:
    """Remove a remote.

    Args:
        name: Name of the remote to remove.
        cwd: Working directory (repository root).
    """
    return run_git_command(['remote', 'remove', name], cwd=cwd)


@tool
def git_tag_create(tag: str, message: str = None, cwd: str = '.') -> Dict:
    """Create a tag.

    Args:
        tag: Name of the tag to create.
        message: Optional annotation message for the tag.
        cwd: Working directory (repository root).
    """
    args = ['tag', '-a', tag, '-m', message] if message else ['tag', tag]
    return run_git_command(args, cwd=cwd)


@tool
def git_tag_list(cwd: str = '.') -> List[str]:
    """List tags.

    Args:
        cwd: Working directory (repository root).
    """
    result = run_git_command(['tag'], cwd=cwd)
    if result['success']:
        return [t.strip() for t in result['stdout'].split('\n') if t.strip()]
    return []


@tool
def git_tag_delete(tag: str, cwd: str = '.') -> Dict:
    """Delete a tag.

    Args:
        tag: Name of the tag to delete.
        cwd: Working directory (repository root).
    """
    return run_git_command(['tag', '-d', tag], cwd=cwd)


@tool
def git_reset(mode: str = 'soft', target: str = 'HEAD', cwd: str = '.') -> Dict:
    """Reset to a commit.

    Args:
        mode: Reset mode ('soft', 'mixed', or 'hard').
        target: Commit hash or reference to reset to.
        cwd: Working directory (repository root).
    """
    return run_git_command(['reset', f'--{mode}', target], cwd=cwd)


@tool
def git_revert(commit_hash: str, cwd: str = '.') -> Dict:
    """Revert a commit.

    Args:
        commit_hash: Hash of the commit to revert.
        cwd: Working directory (repository root).
    """
    return run_git_command(['revert', '--no-edit', commit_hash], cwd=cwd)


@tool
def git_cherry_pick(commit_hash: str, cwd: str = '.') -> Dict:
    """Cherry-pick a commit.

    Args:
        commit_hash: Hash of the commit to cherry-pick.
        cwd: Working directory (repository root).
    """
    return run_git_command(['cherry-pick', commit_hash], cwd=cwd)


@tool
def git_blame(file: str, cwd: str = '.') -> str:
    """Get blame for a file.

    Args:
        file: Path to the file to blame.
        cwd: Working directory (repository root).
    """
    result = run_git_command(['blame', file], cwd=cwd)
    return result['stdout'] if result['success'] else ''


@tool
def git_config_get(key: str, cwd: str = '.') -> str:
    """Get git config value.

    Args:
        key: Config key (e.g. 'user.name').
        cwd: Working directory (repository root).
    """
    result = run_git_command(['config', key], cwd=cwd)
    return result['stdout'] if result['success'] else ''


@tool
def git_config_set(key: str, value: str, cwd: str = '.') -> Dict:
    """Set git config value.

    Args:
        key: Config key (e.g. 'user.name').
        value: Value to set.
        cwd: Working directory (repository root).
    """
    return run_git_command(['config', key, value], cwd=cwd)


@tool
def git_is_repository(path: str = '.') -> bool:
    """Check if path is a git repository.

    Args:
        path: Directory path to check.
    """
    result = run_git_command(['rev-parse', '--is-inside-work-tree'], cwd=path)
    return result['success']


@tool
def git_root(cwd: str = '.') -> str:
    """Get git repository root.

    Args:
        cwd: Working directory inside the repository.
    """
    result = run_git_command(['rev-parse', '--show-toplevel'], cwd=cwd)
    return result['stdout'] if result['success'] else ''


@tool
def git_ignore_add(patterns: List[str], cwd: str = '.') -> str:
    """Add patterns to .gitignore.

    Args:
        patterns: List of gitignore patterns to add.
        cwd: Working directory (repository root).
    """
    gitignore_path = os.path.join(cwd, '.gitignore')
    with open(gitignore_path, 'a') as f:
        for pattern in patterns:
            f.write(pattern + '\n')
    return f"Added {len(patterns)} patterns to .gitignore"


@tool
def git_clean(dry_run: bool = True, cwd: str = '.') -> Dict:
    """Show or remove untracked files.

    Args:
        dry_run: If True, only show files that would be removed (safe preview).
        cwd: Working directory (repository root).
    """
    args = ['clean', '-n' if dry_run else '-f']
    return run_git_command(args, cwd=cwd)
