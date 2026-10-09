"""No server/DB/cloud access: verifies backup failure recovery and retention ordering."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('furniture_backup', Path(__file__).with_name('backup.py'))
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        for folder in ('backend/static', 'frontend/public'):
            (self.project / folder).mkdir(parents=True)
            (self.project / folder / 'photo.jpg').write_bytes(b'photo')
        self.stage = self.root / 'staging'
        self.stage.mkdir()
        self.calls = []

    def fake_run(self, *args, **kwargs):
        self.calls.append(args)
        if args[0] == 'pg_dump':
            Path(args[-1]).write_bytes(b'test dump')
        if args[:2] == ('restic', 'backup'):
            target = kwargs['cwd']
            self.assertTrue((target / 'database.dump').is_file())
            self.assertEqual((target / 'static/photo.jpg').read_bytes(), b'photo')
            self.assertTrue((target / 'public/photo.jpg').is_file())

    def execute(self, fail=None):
        def runner(*args, **kwargs):
            self.fake_run(*args, **kwargs)
            if fail and args[:len(fail)] == fail:
                raise subprocess.CalledProcessError(1, args)
        # os.uname is absent on Windows, but the job only runs on Ubuntu.
        with patch.object(backup, 'run', side_effect=runner), patch.object(
            backup.os, 'uname', create=True
        ) as uname:
            uname.return_value.nodename = 'test-vps'
            backup.backup(self.project, self.stage, 'furniture-backend.service')

    def test_success_restarts_before_upload_and_prunes_after_upload(self):
        self.execute()
        prefixes = [call[:2] for call in self.calls]
        self.assertLess(prefixes.index(('systemctl', 'start')), prefixes.index(('restic', 'backup')))
        self.assertLess(prefixes.index(('restic', 'backup')), prefixes.index(('restic', 'forget')))
        self.assertEqual(list(self.stage.iterdir()), [])

    def test_dump_failure_restarts_and_preserves_remote_backups(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.execute(('pg_dump',))
        self.assertIn(('systemctl', 'start', 'furniture-backend.service'), self.calls)
        self.assertFalse(any(call[:2] == ('restic', 'forget') for call in self.calls))
        self.assertEqual(list(self.stage.iterdir()), [])

    def test_upload_failure_does_not_prune(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.execute(('restic', 'backup'))
        self.assertFalse(any(call[:2] == ('restic', 'forget') for call in self.calls))

    def test_repository_failure_does_not_stop_backend(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.execute(('restic', 'snapshots'))
        self.assertFalse(any(call[0] == 'systemctl' for call in self.calls))

    def test_inactive_backend_is_not_started(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.execute(('systemctl', 'is-active'))
        self.assertNotIn(('systemctl', 'start', 'furniture-backend.service'), self.calls)


if __name__ == '__main__':
    unittest.main()
