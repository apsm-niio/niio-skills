"""Transactional per-user skills + stdio MCP setup, update, authentication and rollback."""
import argparse,base64,contextlib,ctypes,getpass,hashlib,json,os,pathlib,re,shutil,subprocess,sys,tempfile,uuid
import install_bundle as installer

ROOT=pathlib.Path(__file__).resolve().parents[1]
UPSTREAM='https://niiodemo.apsm.com.tw/mcp'

def json_read(p):return json.loads(pathlib.Path(p).read_text(encoding='utf8'))
def validate_path(p):
    p=pathlib.Path(p).absolute()
    for x in [p,*p.parents]:
        if x.exists() and (x.is_symlink() or getattr(x.lstat(),'st_file_attributes',0)&0x400):raise ValueError('Linked installation path rejected')
    return p

def private_dir(p):
    fresh=not p.exists();p.mkdir(parents=True,exist_ok=True,mode=0o700)
    if fresh and os.name=='nt':
        raw=subprocess.check_output(['whoami','/user','/fo','csv','/nh'])
        sid=re.search(rb'S-\d-\d+(?:-\d+)+',raw).group().decode('ascii')
        subprocess.run(['icacls',str(p),'/inheritance:r','/grant:r','*'+sid+':(OI)(CI)F'],capture_output=True,check=True)

@contextlib.contextmanager
def locked(base):
    private_dir(base);lock=base/'.install.lock'
    with lock.open('x'):pass
    try:yield
    finally:lock.unlink()

def node_path(value=None):
    found=value or shutil.which('node')
    if not found:raise ValueError('Install Node.js 24 LTS or newer, then retry')
    node=str(pathlib.Path(found).resolve())
    version=subprocess.check_output([node,'--version'],text=True).strip()
    if not re.fullmatch(r'v\d+\.\d+\.\d+',version) or int(version[1:].split('.')[0])<24:raise ValueError('Node.js 24 LTS or newer is required; Node 22.12 has a reproduced Windows Unicode-path SDK crash')
    return node

def config_op(node,runtime,args):
    r=subprocess.run([node,str(runtime/'scripts/config-transaction.mjs')],input=json.dumps(args).encode('utf8'),capture_output=True,timeout=30)
    if r.returncode:
        # Child errors are fixed identifiers; do not echo configuration or credentials.
        message=r.stderr.decode(errors='replace').strip()
        raise ValueError(message if re.fullmatch('[A-Z_]+',message) else 'CONFIG_OPERATION_FAILED')
    return json.loads(r.stdout)

def runtime_source(source):return source/'mcp/niio-local-mcp'
def verify_source_manifest(source):
    manifest=source/'niio-bundle-manifest.json'
    if not manifest.exists():return
    entries=json_read(manifest)['files']
    for name,digest in entries.items():
        rel=pathlib.PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Invalid bundle manifest')
        path=source/name
        if not path.resolve().is_relative_to(source.resolve()) or not path.is_file() or path.is_symlink():raise ValueError('Invalid bundle path')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Bundle integrity mismatch: '+name)
    actual=installer.inventory(source)
    actual.pop('niio-bundle-manifest.json',None)
    if actual!=entries:raise ValueError('Unexpected/missing files in reviewed bundle')

def source_digest(source):
    verify_source_manifest(source)
    app={k:v for k,v in installer.inventory(runtime_source(source)).items() if not k.startswith('node_modules/')}
    data={'skills':installer.inventory(source/'skills'),'runtime':app}
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()

def ensure_dependencies(runtime,node):
    if (runtime/'node_modules/@modelcontextprotocol/sdk/package.json').is_file():return
    npm=pathlib.Path(node).with_name('npm.cmd' if os.name=='nt' else 'npm')
    if not npm.exists():raise ValueError('npm missing; use the reviewed offline ZIP or install Node with npm')
    if os.name=='nt':
        # npm's JS entry avoids invoking cmd.exe or shell interpolation.
        cli=pathlib.Path(node).parent/'node_modules/npm/bin/npm-cli.js'
        if not cli.exists():raise ValueError('npm CLI missing beside Node')
        cmd=[node,str(cli)]
    else:cmd=[str(npm)]
    r=subprocess.run(cmd+['ci','--ignore-scripts','--no-audit','--no-fund','--bin-links=false'],cwd=runtime,capture_output=True,timeout=180)
    if r.returncode:raise ValueError('DEPENDENCY_INSTALL_FAILED; live skills and config not changed')

def ensure_runtime_load(runtime,node):
    r=subprocess.run([node,'--input-type=module','-e',"await import('./src/server.mjs');console.log('NIIO_RUNTIME_LOAD_OK');"],cwd=runtime,capture_output=True,timeout=30)
    if r.returncode or r.stdout.strip()!=b'NIIO_RUNTIME_LOAD_OK':
        raise ValueError('RUNTIME_LOAD_FAILED: use a shorter --codex-home path or a compatible Node version; live skills/config have not changed')

def check_release(data,base):
    release=validate_path(data['releaseDir'])
    if release.parent!=base/'releases' or not re.fullmatch('[0-9a-f]{20}',release.name):raise ValueError('Invalid managed release path')
    if installer.inventory(release)!=data['releaseHashes']:raise ValueError('Modified managed runtime/baseline blocks operation')
    return release

def receipt_load(path):
    path=validate_path(path);data=json_read(path)
    if data.get('kind')!='niio-skills-and-local-mcp':raise ValueError('Not a combined bundle receipt')
    home=validate_path(data['codexHome']);base=home/'niio-local-mcp'
    if path.parent.parent!=base/'receipts' or path.name!='receipt.json':raise ValueError('Receipt outside managed directory')
    if pathlib.Path(data['skillReceipt']).parent.parent!=home:raise ValueError('Skill receipt outside expected home')
    if pathlib.Path(data['skillReceipt']).name!='receipt.json' or not pathlib.Path(data['skillReceipt']).parent.name.startswith('.niio-backup-'):raise ValueError('Invalid skill receipt')
    return path,data,home,base

def current_state(base):return json_read(base/'state.json') if (base/'state.json').exists() else None

def validate_installed(data,home,base):
    release=check_release(data,base)
    child=json_read(data['skillReceipt'])
    if child['state']!='installed':raise ValueError('Skill transaction is not installed')
    for item in child['entries']:
        if installer.inventory(home/'skills'/item['name'])!=item['hashes']:raise ValueError('Customized skill blocks update: '+item['name'])
    c=config_op(data['node'],release/'runtime',{'op':'verify','path':str(home/'config.toml')})
    if c['blockHash']!=data['configMeta']['blockHash']:raise ValueError('Customized MCP entry blocks update')
    return release

def setup(source,home,node=None,baseline=None,reuse_existing_auth=False,legacy_config=None,adopt=False):
    source=validate_path(source);home=validate_path(home);home.mkdir(parents=True,exist_ok=True)
    node=node_path(node);base=home/'niio-local-mcp';digest=source_digest(source)
    with locked(base):
        old=current_state(base);old_data=None
        if old:
            _,old_data,old_home,_=receipt_load(old['receipt'])
            if old_home!=home:raise ValueError('Managed home mismatch')
            validate_installed(old_data,home,base)
            baseline=pathlib.Path(old_data['releaseDir'])
            reuse_existing_auth=bool(old_data.get('legacyConfig')) if not reuse_existing_auth else True
            legacy_config=legacy_config or old_data.get('legacyConfig')
        if reuse_existing_auth:
            legacy_config=validate_path(legacy_config or home/'config.toml')
            if not legacy_config.is_file():raise ValueError('Existing credential configuration not found')
        else:legacy_config=None
        if old_data and old_data['sourceDigest']==digest and old_data['node']==node and old_data.get('legacyConfig')==(str(legacy_config) if legacy_config else None):
            return pathlib.Path(old['receipt'])
        for name,path in installer.skills(source).items():
            dest=home/'skills'/name
            if dest.exists() and (not baseline or name not in installer.skills(baseline) or installer.inventory(dest)!=installer.inventory(installer.skills(baseline)[name])):
                raise ValueError('Existing/custom skill requires its reviewed --baseline: '+name)
        release=base/'releases'/digest[:20];(base/'releases').mkdir(exist_ok=True)
        if not release.exists():
            stage=pathlib.Path(tempfile.mkdtemp(prefix='.stage-',dir=base))
            try:
                shutil.copytree(runtime_source(source),stage/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
                shutil.copytree(source/'skills',stage/'skills',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
                ensure_dependencies(stage/'runtime',node)
                installer.inventory(stage)
                stage.rename(release)
                try:ensure_runtime_load(release/'runtime',node)
                except Exception:
                    if release.resolve().parent!=(base/'releases').resolve() or release.name!=digest[:20] or release.is_symlink():raise ValueError('Unsafe failed-release cleanup rejected')
                    installer.inventory(release)
                    shutil.rmtree(release)
                    raise
            finally:
                if stage.exists():
                    if stage.resolve().parent!=base.resolve() or not stage.name.startswith('.stage-'):raise ValueError('Unsafe staging cleanup rejected')
                    shutil.rmtree(stage)
            index=base/'release-manifests';index.mkdir(exist_ok=True)
            installer.write_receipt(index/(digest+'.json'),{'sourceDigest':digest,'hashes':installer.inventory(release)})
        else:
            manifest_path=base/'release-manifests'/(digest+'.json')
            if not manifest_path.exists() or json_read(manifest_path)!={'sourceDigest':digest,'hashes':installer.inventory(release)}:
                raise ValueError('Unowned/modified existing release blocks setup')
            ensure_runtime_load(release/'runtime',node)
        ident=uuid.uuid4().hex;folder=base/'receipts'/ident;private_dir(folder)
        receipt=folder/'receipt.json';skill_receipt=home/('.niio-backup-'+ident)/'receipt.json'
        env={'NIIO_LOCAL_HOME':str(base)}
        if legacy_config:env['NIIO_LEGACY_CODEX_CONFIG']=str(legacy_config)
        entry={'command':node,'args':[str(release/'runtime/src/server.mjs')],'cwd':str(release/'runtime'),'env':env,'env_vars':['NIIO_LOCAL_TOKEN'],'startup_timeout_sec':30,'tool_timeout_sec':120}
        data={'kind':'niio-skills-and-local-mcp','schemaVersion':1,'state':'preparing','codexHome':str(home),'node':node,'sourceDigest':digest,'releaseDir':str(release),'releaseHashes':installer.inventory(release),'skillReceipt':str(skill_receipt),'previousState':old,'legacyConfig':str(legacy_config) if legacy_config else None}
        installer.write_receipt(receipt,data)
        meta=config_op(node,release/'runtime',{'op':'prepare','path':str(home/'config.toml'),'entry':entry,'dir':str(folder),'adopt':adopt})
        data['configMeta']=meta;data['state']='installing';installer.write_receipt(receipt,data)
        try:
            installer.install(release,home/'skills',baseline,backup_dir=skill_receipt.parent)
            config_op(node,release/'runtime',{'op':'apply','path':str(home/'config.toml'),'dir':str(folder),'meta':meta})
            installer.write_receipt(base/'state.json',{'receipt':str(receipt)})
            data['state']='installed';installer.write_receipt(receipt,data)
            return receipt
        except Exception as exc:
            try:restore(receipt,locked_already=True)
            except Exception as recovery:raise OSError('Combined install/restore interrupted; resume restore using receipt '+str(receipt)) from recovery
            raise exc

def restore(path,locked_already=False):
    receipt,data,home,base=receipt_load(path)
    with contextlib.nullcontext() if locked_already else locked(base):
        release=check_release(data,base);state=current_state(base)
        if state not in (None,{'receipt':str(receipt)},data['previousState']):raise ValueError('A newer installation must be restored first')
        if 'configMeta' not in data:raise ValueError('Incomplete preparation; no live changes were made')
        config_op(data['node'],release/'runtime',{'op':'check','path':str(home/'config.toml'),'dir':str(receipt.parent),'meta':data['configMeta']})
        child_path=pathlib.Path(data['skillReceipt'])
        if child_path.exists():
            child=json_read(child_path)
            for e in child['entries']:installer.restore_stage(e,home/'skills',child_path.parent)
        data['state']='restoring';installer.write_receipt(receipt,data)
        if child_path.exists():installer.restore(child_path)
        config_op(data['node'],release/'runtime',{'op':'restore','path':str(home/'config.toml'),'dir':str(receipt.parent),'meta':data['configMeta']})
        if data['previousState']:installer.write_receipt(base/'state.json',data['previousState'])
        elif (base/'state.json').exists():(base/'state.json').unlink()
        data['state']='restored';installer.write_receipt(receipt,data)

def verify(home,credential_file=None):
    home=validate_path(home);base=home/'niio-local-mcp';state=current_state(base)
    if not state:raise ValueError('No combined installation')
    _,data,_,_=receipt_load(state['receipt']);release=validate_installed(data,home,base)
    env=dict(os.environ)
    if credential_file:env['NIIO_LOCAL_CREDENTIAL_FILE']=str(credential_file)
    r=subprocess.run([data['node'],str(release/'runtime/scripts/verify.mjs'),str(home/'config.toml')],env=env,capture_output=True,timeout=90)
    if r.returncode:raise ValueError('NIIO_VERIFY_FAILED_CHECK_AUTH_AND_UPSTREAM')
    return json.loads(r.stdout)

def encrypt_windows(value):
    if os.name!='nt':raise ValueError('Secure persistent PAT storage supports Windows; use NIIO_LOCAL_TOKEN environment elsewhere')
    class Blob(ctypes.Structure):_fields_=[('cbData',ctypes.c_ulong),('pbData',ctypes.POINTER(ctypes.c_ubyte))]
    buf=ctypes.create_string_buffer(value.encode('utf8'));inp=Blob(len(value.encode('utf8')),ctypes.cast(buf,ctypes.POINTER(ctypes.c_ubyte)));out=Blob()
    protect=ctypes.windll.crypt32.CryptProtectData;protect.argtypes=[ctypes.POINTER(Blob),ctypes.c_wchar_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong,ctypes.POINTER(Blob)];protect.restype=ctypes.c_int
    if not protect(ctypes.byref(inp),'niio local MCP',None,None,None,1,ctypes.byref(out)):raise ValueError('DPAPI_ENCRYPTION_FAILED')
    try:return base64.b64encode(ctypes.string_at(out.pbData,out.cbData)).decode('ascii')
    finally:
        free=ctypes.windll.kernel32.LocalFree;free.argtypes=[ctypes.c_void_p];free.restype=ctypes.c_void_p
        free(ctypes.cast(out.pbData,ctypes.c_void_p))

def authenticate(home):
    home=validate_path(home);base=home/'niio-local-mcp'
    if not current_state(base):raise ValueError('Run setup before authentication')
    if not sys.stdin.isatty():raise ValueError('Use an interactive terminal for hidden PAT entry; never pass a token as an argument')
    token=getpass.getpass('niio personal PAT (hidden): ').strip()
    if not re.fullmatch(r'\S{1,4096}',token):raise ValueError('Invalid PAT format')
    store={'version':1,'upstreamUrl':UPSTREAM,'protection':'windows-dpapi-current-user','ciphertext':encrypt_windows(token)}
    del token
    with locked(base):
        temp=base/('auth-check-'+uuid.uuid4().hex+'.json')
        try:
            installer.write_receipt(temp,store);result=verify(home,temp)
            os.replace(temp,base/'auth.json');return result
        finally:
            if temp.exists():temp.unlink()

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    for action in ['setup','update']:
        a=sub.add_parser(action);a.add_argument('--source',type=pathlib.Path,default=ROOT);a.add_argument('--codex-home',type=pathlib.Path,default=pathlib.Path.home()/'.codex');a.add_argument('--node');a.add_argument('--baseline',type=pathlib.Path);a.add_argument('--reuse-existing-auth',action='store_true');a.add_argument('--legacy-config',type=pathlib.Path);a.add_argument('--adopt-existing-local',action='store_true')
    a=sub.add_parser('restore');a.add_argument('--receipt',type=pathlib.Path,required=True)
    for action in ['auth','verify']:
        a=sub.add_parser(action);a.add_argument('--codex-home',type=pathlib.Path,default=pathlib.Path.home()/'.codex')
    a=p.parse_args(argv)
    try:
        if a.action in ['setup','update']:
            if a.action=='update' and not current_state(validate_path(a.codex_home)/'niio-local-mcp'):raise ValueError('Run setup for first installation')
            receipt=setup(a.source,a.codex_home,a.node,a.baseline,a.reuse_existing_auth,a.legacy_config,a.adopt_existing_local)
            installed=json_read(receipt)
            authentication='existing per-user source selected' if installed.get('legacyConfig') else 'credential store retained; run verify' if (a.codex_home/'niio-local-mcp/auth.json').exists() else 'run auth, then verify; installation alone is not authentication'
            print(json.dumps({'installed':True,'receipt':str(receipt),'authentication':authentication,'restartAgentRequired':True}))
        elif a.action=='restore':restore(a.receipt);print(json.dumps({'restored':True,'backupsAndCredentialsRetained':True,'restartAgentRequired':True}))
        elif a.action=='verify':print(json.dumps(verify(a.codex_home)))
        else:print(json.dumps(authenticate(a.codex_home)))
    except ValueError as exc:
        p.exit(1,'NIIO_BUNDLE_OPERATION_BLOCKED: '+str(exc)+'\n')
    except OSError as exc:
        if str(exc).startswith('Combined install/restore interrupted;'):
            p.exit(1,str(exc)+'\n')
        p.exit(1,'NIIO_BUNDLE_FILESYSTEM_BLOCKED: preserve receipt/backups; check permissions, locks and paths.\n')
    except (KeyError,subprocess.SubprocessError):
        p.exit(1,'NIIO_BUNDLE_OPERATION_BLOCKED: check Node/npm and the installation receipt; no credential output is logged.\n')

if __name__=='__main__':main()
