import importlib.util,json,os,pathlib,shutil,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import manage_local_bundle as bundle

class LocalBundleTests(unittest.TestCase):
 def setUp(self):
  self.node=bundle.node_path(os.environ.get('NIIO_TEST_NODE'))
  self.temp=tempfile.TemporaryDirectory(prefix='niio-local-bundle-');self.root=pathlib.Path(self.temp.name)
  self.source=self.root/'source';self.home=self.root/'codex';self.home.mkdir()
  for i in range(8):
   p=self.source/'skills/category'/('niio-test-'+str(i));p.mkdir(parents=True);(p/'SKILL.md').write_text('old '+str(i))
  app=self.source/'mcp/niio-local-mcp';(app/'scripts').mkdir(parents=True);(app/'src').mkdir()
  (app/'src/server.mjs').write_text('// synthetic installer fixture, not an MCP server\n')
  shutil.copyfile(ROOT/'mcp/niio-local-mcp/scripts/config-transaction.mjs',app/'scripts/config-transaction.mjs')
  modules=app/'node_modules';shutil.copytree(ROOT/'mcp/niio-local-mcp/node_modules/smol-toml',modules/'smol-toml')
  sdk=modules/'@modelcontextprotocol/sdk';sdk.mkdir(parents=True);(sdk/'package.json').write_text('{}')
  self.original='model = "keep-existing-model"\n\n[mcp_servers.unrelated]\nurl = "https://example.invalid/mcp"\n'
  (self.home/'config.toml').write_text(self.original,encoding='utf8')
 def tearDown(self):self.temp.cleanup()
 def setup(self,**kw):return bundle.setup(self.source,self.home,node=self.node,**kw)
 def test_fresh_install_and_restore_preserve_unrelated_config_and_skills(self):
  extra=self.home/'skills/custom';extra.mkdir(parents=True);(extra/'SKILL.md').write_text('keep')
  receipt=self.setup();self.assertEqual(len(list((self.home/'skills').glob('niio-*/SKILL.md'))),8)
  state=json.loads(receipt.read_text());self.assertEqual(state['state'],'installed')
  config=(self.home/'config.toml').read_text();self.assertIn('niio_local_mcp',config);self.assertIn('unrelated',config)
  self.assertNotIn('Authorization',config)
  bundle.restore(receipt);self.assertEqual((self.home/'config.toml').read_text(),self.original)
  self.assertEqual((extra/'SKILL.md').read_text(),'keep');bundle.restore(receipt)
 def test_update_rollback_and_reapply_existing_managed_release(self):
  first=self.setup();old=json.loads(first.read_text())['releaseDir']
  (self.source/'skills/category/niio-test-0/SKILL.md').write_text('new')
  second=self.setup();self.assertNotEqual(json.loads(second.read_text())['releaseDir'],old)
  bundle.restore(second);self.assertEqual((self.home/'skills/niio-test-0/SKILL.md').read_text(),'old 0')
  self.assertIn(old,(self.home/'config.toml').read_text().replace('\\\\','\\'))
  third=self.setup();self.assertEqual((self.home/'skills/niio-test-0/SKILL.md').read_text(),'new')
  bundle.restore(third);bundle.restore(first)
 def test_unrelated_configuration_edits_survive_restore(self):
  receipt=self.setup();p=self.home/'config.toml';p.write_text(p.read_text()+'\n[features]\nkeep_new_setting = true\n')
  bundle.restore(receipt);self.assertIn('keep_new_setting = true',p.read_text());self.assertIn('unrelated',p.read_text());self.assertNotIn('niio_local_mcp',p.read_text())
 def test_custom_skill_prevents_update_without_changing_config(self):
  receipt=self.setup();p=self.home/'skills/niio-test-0/custom.txt';p.write_text('keep')
  config=(self.home/'config.toml').read_bytes()
  (self.source/'skills/category/niio-test-1/SKILL.md').write_text('new')
  with self.assertRaises(ValueError):self.setup()
  self.assertEqual((self.home/'config.toml').read_bytes(),config);self.assertEqual(p.read_text(),'keep')
 def test_custom_local_entry_blocks_restore_before_skill_changes(self):
  receipt=self.setup();p=self.home/'config.toml';p.write_text(p.read_text().replace('tool_timeout_sec = 120','tool_timeout_sec = 121'))
  with self.assertRaises(ValueError):bundle.restore(receipt)
  self.assertTrue((self.home/'skills/niio-test-0/SKILL.md').exists())
 def test_concurrent_config_edit_during_setup_rolls_skills_back(self):
  original=bundle.config_op
  def racing(node,runtime,args):
   if args['op']=='apply':
    p=self.home/'config.toml';p.write_text(p.read_text()+'\n[features]\nracing = true\n')
   return original(node,runtime,args)
  with patch.object(bundle,'config_op',racing):
   with self.assertRaises(ValueError):self.setup()
  self.assertEqual(list((self.home/'skills').glob('niio-*')),[])
  self.assertIn('racing = true',(self.home/'config.toml').read_text());self.assertFalse((self.home/'niio-local-mcp/state.json').exists())
 def test_interrupted_restore_resumes_after_skills_moved(self):
  receipt=self.setup();original=bundle.config_op;failed=[False]
  def fail_once(node,runtime,args):
   if args['op']=='restore' and not failed[0]:failed[0]=True;raise OSError('simulated config write failure')
   return original(node,runtime,args)
  with patch.object(bundle,'config_op',fail_once):
   with self.assertRaises(OSError):bundle.restore(receipt)
  bundle.restore(receipt);self.assertEqual((self.home/'config.toml').read_text(),self.original)
  self.assertEqual(json.loads(receipt.read_text())['state'],'restored')
 def test_existing_manual_local_entry_requires_adoption_and_restores_exactly(self):
  p=self.home/'config.toml';old=self.original+'\n[mcp_servers.niio_local_mcp]\ncommand = "old-node"\nargs = ["old-server"]\n'
  p.write_text(old)
  with self.assertRaises(ValueError):self.setup()
  self.assertEqual(p.read_text(),old)
  # The failed preparation retained an unowned immutable release with a recorded manifest.
  receipt=self.setup(adopt=True);bundle.restore(receipt);self.assertEqual(p.read_text(),old)
 def test_absent_config_is_removed_on_first_install_restore(self):
  (self.home/'config.toml').unlink();receipt=self.setup();bundle.restore(receipt)
  self.assertFalse((self.home/'config.toml').exists())
 def test_adopting_disabled_service_preserves_disabled_state_across_update(self):
  p=self.home/'config.toml';old=self.original+'\n[mcp_servers.niio_local_mcp]\nenabled = false\ncommand = "old-node"\nargs = ["old-server"]\n'
  p.write_text(old)
  first=self.setup(adopt=True);self.assertIn('enabled = false',p.read_text())
  (self.source/'skills/category/niio-test-0/SKILL.md').write_text('next')
  second=self.setup();self.assertIn('enabled = false',p.read_text())
  bundle.restore(second);bundle.restore(first);self.assertEqual(p.read_text(),old)
 def test_modified_runtime_blocks_restore(self):
  receipt=self.setup();d=json.loads(receipt.read_text());(pathlib.Path(d['releaseDir'])/'runtime/src/server.mjs').write_text('custom')
  with self.assertRaises(ValueError):bundle.restore(receipt)
  self.assertIn('niio_local_mcp',(self.home/'config.toml').read_text())
 def test_unusable_runtime_fails_before_live_skills_and_config_change(self):
  with patch.object(bundle,'ensure_runtime_load',side_effect=ValueError('RUNTIME_LOAD_FAILED')):
   with self.assertRaises(ValueError):self.setup()
  self.assertEqual((self.home/'config.toml').read_text(),self.original)
  self.assertEqual(list((self.home/'skills').glob('niio-*')) if (self.home/'skills').exists() else [],[])
  self.assertFalse((self.home/'niio-local-mcp/state.json').exists())
 def test_changed_configuration_backup_blocks_restore_before_skill_moves(self):
  receipt=self.setup();(receipt.parent/'config.before.toml').write_text('model="unexpected"\n')
  with self.assertRaises(ValueError):bundle.restore(receipt)
  self.assertTrue((self.home/'skills/niio-test-0/SKILL.md').exists())
  self.assertIn('niio_local_mcp',(self.home/'config.toml').read_text())

if __name__=='__main__':unittest.main()
