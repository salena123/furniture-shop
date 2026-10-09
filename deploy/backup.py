"""Ubuntu backup job. Credentials come from a root-only systemd EnvironmentFile.

Copies data while the backend is stopped, then restarts it before network upload.
Only temporary files created by this script are removed locally.
"""
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def snapshot(project, target, service):
    # Refuse to start a backend that was intentionally stopped before this job.
    run('systemctl', 'is-active', '--quiet', service)
    try:
        run('systemctl', 'stop', service)
        run('pg_dump', '--no-password', '--format=custom', '--file', str(target / 'database.dump'))
        run('pg_restore', '--list', str(target / 'database.dump'), stdout=subprocess.DEVNULL)
        shutil.copytree(project / 'backend/static', target / 'static')
        shutil.copytree(project / 'frontend/public', target / 'public')
        config = target / 'config'
        config.mkdir()
        for source, name in (
            (project / '.env', 'project.env'),
            (project / 'backend/.env', 'backend.env'),
            (Path('/etc/caddy/Caddyfile'), 'Caddyfile'),
        ):
            if source.is_file():
                shutil.copy2(source, config / name)
    finally:
        # Also restart after a failed dump/copy; never wait for the remote upload.
        run('systemctl', 'start', service)


def backup(project, staging, service):
    for directory in ('backend/static', 'frontend/public'):
        if not (project / directory).is_dir():
            raise RuntimeError(f'Missing directory: {directory}')
    # Verify access to the initialized remote repository before stopping the app.
    run('restic', 'snapshots', '--quiet', stdout=subprocess.DEVNULL)
    with tempfile.TemporaryDirectory(prefix='snapshot-', dir=staging) as temporary:
        target = Path(temporary)
        snapshot(project, target, service)
        # Relative paths make all snapshots share stable paths despite temp names.
        run('restic', 'backup', '--tag', 'furniture-shop', '.', cwd=target)
    # Only prune after a completely successful backup, and only this host/tag.
    run('restic', 'forget', '--host', os.uname().nodename, '--tag', 'furniture-shop',
        '--group-by', 'host,tags', '--keep-daily', '7', '--keep-weekly', '4', '--prune')
    run('restic', 'check')
    print('Backup, retention and repository metadata check completed.', flush=True)


def main():
    import fcntl  # Ubuntu only; helpers remain testable on Windows.

    os.umask(0o077)
    required = ('RESTIC_REPOSITORY', 'RESTIC_PASSWORD_FILE', 'PGHOST', 'PGDATABASE',
                'PGUSER', 'PGPASSFILE', 'APP_DIR', 'BACKEND_SERVICE')
    if any(not os.environ.get(key) for key in required):
        raise RuntimeError('Fill in /etc/furniture-backup.env first')
    # The template intentionally supports only external S3 over HTTPS.
    if not os.environ['RESTIC_REPOSITORY'].startswith('s3:https://'):
        raise RuntimeError('Use a separate S3 repository over HTTPS')
    staging = Path('/var/lib/furniture-backup')
    staging.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (staging / 'job.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        backup(Path(os.environ['APP_DIR']).resolve(), staging, os.environ['BACKEND_SERVICE'])


def terminate(signum, frame):
    raise SystemExit(128 + signum)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, terminate)
    main()
