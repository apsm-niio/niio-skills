import json,os,pathlib,subprocess,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import manage_local_bundle as bundle

@unittest.skipUnless(os.name=='nt','CurrentUser DPAPI is a Windows feature')
class LocalCredentialsTests(unittest.TestCase):
 def test_dpapi_ciphertext_roundtrip_without_plaintext_file(self):
  with tempfile.TemporaryDirectory(prefix='niio-dpapi-') as tmp:
   p=pathlib.Path(tmp);token='synthetic-unit-credential-not-a-real-pat'
   store={'version':1,'upstreamUrl':bundle.UPSTREAM,'protection':'windows-dpapi-current-user','ciphertext':bundle.encrypt_windows(token)}
   raw=json.dumps(store);self.assertNotIn(token,raw);(p/'auth.json').write_text(raw,encoding='utf8')
   script="import {currentHeaders} from './src/credentials.mjs';const h=await currentHeaders();console.log(JSON.stringify({matches:h.Authorization==='Bearer synthetic-unit-credential-not-a-real-pat'}));"
   env={**os.environ,'NIIO_LOCAL_HOME':str(p),'NIIO_LOCAL_CREDENTIAL_FILE':str(p/'auth.json')}
   r=subprocess.run([bundle.node_path(os.environ.get('NIIO_TEST_NODE')),'--input-type=module','-e',script],cwd=ROOT/'mcp/niio-local-mcp',env=env,capture_output=True)
   self.assertEqual(r.returncode,0);self.assertTrue(json.loads(r.stdout)['matches']);self.assertNotIn(token,r.stdout.decode())
 def test_failed_new_credential_validation_preserves_old_store(self):
  with tempfile.TemporaryDirectory(prefix='niio-auth-') as tmp:
   home=pathlib.Path(tmp);base=home/'niio-local-mcp';base.mkdir()
   (base/'state.json').write_text('{}');old=b'{"old":"encrypted-data-placeholder"}';(base/'auth.json').write_bytes(old)
   with patch.object(sys.stdin,'isatty',return_value=True),patch.object(bundle.getpass,'getpass',return_value='synthetic-not-real'),patch.object(bundle,'verify',side_effect=ValueError('denied')):
    with self.assertRaises(ValueError):bundle.authenticate(home)
   self.assertEqual((base/'auth.json').read_bytes(),old);self.assertEqual(list(base.glob('auth-check-*')),[])

if __name__=='__main__':unittest.main()
