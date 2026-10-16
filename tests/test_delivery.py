import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
installer = load('bundle', 'scripts/install_bundle.py')
view = load('view_project', 'localization/overrides/deployment-guides/api/niio-view-plugin/scripts/view_project.py')
capture = load('capture', 'acceptance/check_capture.py')


class DeliveryTests(unittest.TestCase):
    def test_scan_requires_explicit_root_and_defaults_offline(self):
        script=ROOT/'skills/mcp/niio-mcp-app-builder/plan/scripts/scan_apps.py'
        result=subprocess.run([sys.executable,str(script)],capture_output=True)
        self.assertNotEqual(result.returncode,0)
        with tempfile.TemporaryDirectory() as tmp:
            result=subprocess.run([sys.executable,str(script),tmp],capture_output=True)
            self.assertEqual(result.returncode,0)
            self.assertEqual(json.loads(result.stdout),{'apps':[]})

    def test_install_restore_all_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)/'skills'
            receipt = installer.install(ROOT, dest)
            self.assertEqual(len(list(dest.glob('*/SKILL.md'))), 8)
            for name, source in installer.skills(ROOT).items():
                self.assertEqual(installer.inventory(source), installer.inventory(dest/name))
            installer.restore(receipt)
            self.assertEqual(list(dest.glob('*/SKILL.md')), [])
            installer.restore(receipt)

    def test_update_restore_and_custom_file_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'skills'
            installer.install(ROOT, dest)
            before={n:installer.inventory(p) for n,p in installer.skills(ROOT).items()}
            receipt=installer.install(ROOT, dest, ROOT)
            installer.restore(receipt)
            self.assertEqual(before, {n:installer.inventory(dest/n) for n in before})
            custom=dest/'niio-cli'/'notes.txt'
            custom.write_text('keep')
            with self.assertRaises(ValueError): installer.install(ROOT, dest, ROOT)
            self.assertEqual(custom.read_text(),'keep')

    def test_interrupted_install_rolls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'skills'
            installer.install(ROOT,dest)
            original=Path.rename
            count=[0]
            def fail_once(path, target):
                count[0]+=1
                if count[0]==4: raise OSError('simulated interrupted rename')
                return original(path,target)
            with patch.object(Path,'rename',fail_once):
                with self.assertRaises(OSError): installer.install(ROOT,dest,ROOT)
            for name,source in installer.skills(ROOT).items():
                self.assertEqual(installer.inventory(source),installer.inventory(dest/name))

    def test_restore_refuses_changed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'skills'; receipt=installer.install(ROOT,dest)
            changed=dest/'niio-cli'/'SKILL.md'; changed.write_text('custom')
            with self.assertRaises(ValueError): installer.restore(receipt)
            self.assertEqual(changed.read_text(),'custom')

    def test_view_inputs_and_missing_dependencies(self):
        self.assertEqual(view.plan('sheet-view','React','https://api.example.test/v3/','https://ui.example.test/')[4], 'sheet-view')
        for identifier in ('sheet-time-random','', 'sheet/../../view'):
            with self.assertRaises(ValueError): view.plan(identifier,'React','https://api.example.test','https://ui.example.test')
        for host in ('https://example.invalid','https://user:password@example.test','http://example.test'):
            with self.assertRaises(ValueError): view.url(host)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'src').mkdir()
            (p/'mdye.json').write_text(json.dumps(dict(id='sheet-view',template='React',host='https://api.example.test',webui='https://ui.example.test')))
            (p/'package.json').write_text('{}')
            with self.assertRaises(ValueError): view.preflight(p)
            (p/'node_modules').mkdir()
            self.assertEqual(view.preflight(p)['status'],'preflight-only')

    def test_capture_positive_and_negative(self):
        for channel in ('api','cli','website','view'):
            c=dict(channel=channel,successPath=['success'],successValue=True,rowsPath=['data','rows'], minRows=1,maxRows=1,allowedFields=['rowid','name'],target='fixture-only')
            r=dict(status=200,contentType='application/json',target='fixture-only',body={'success':True,'data':{'rows':[{'rowid':'mock','name':'Mock'}]}})
            self.assertEqual(capture.check(c,r)['rows'],1)
            for bad in ({'status':404}, {'contentType':'text/html'}, {'target':'wrong'}, {'body':{'data':[]}}, {'body':{**r['body'],'success':False}}):
                with self.assertRaises(ValueError): capture.check(c,{**r,**bad})


if __name__=='__main__': unittest.main()
