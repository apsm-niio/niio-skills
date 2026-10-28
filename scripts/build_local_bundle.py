"""Build the reviewed offline ZIP with skills, stdio source, lockfile and JS dependencies."""
import hashlib,json,pathlib,shutil,subprocess,tempfile,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]

def build(output=None):
    runtime=ROOT/'mcp/niio-local-mcp'
    if not (runtime/'node_modules/@modelcontextprotocol/sdk/package.json').exists():
        raise ValueError('Run npm ci --ignore-scripts --no-audit --no-fund --bin-links=false in mcp/niio-local-mcp first')
    output=pathlib.Path(output or ROOT/'dist/niio-skills-local-mcp-20261028.zip').resolve();output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='niio-bundle-build-',dir=output.parent) as tmp:
        stage=pathlib.Path(tmp)/'niio-skills';stage.mkdir()
        for name in ['skills','scripts','docs','acceptance','assets','localization','tests','mcp']:
            shutil.copytree(ROOT/name,stage/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo','.pytest_cache'))
        for name in ['README.md','THIRD_PARTY_LICENSE.txt','requirements-validation.txt','.gitattributes']:
            shutil.copyfile(ROOT/name,stage/name)
        files={}
        for p in stage.rglob('*'):
            if p.is_symlink():raise ValueError('Linked bundle content rejected')
            if not p.is_file():continue
            rel=p.relative_to(stage).as_posix()
            if any(part in ['.git','.codex','.ssh','evidence','.validation-temp'] for part in p.relative_to(stage).parts):raise ValueError('Private artifact in bundle')
            if p.name in ['auth.json','config.toml','receipt.json'] or p.suffix in ['.key','.pfx','.p12']:raise ValueError('Credential/config artifact in bundle')
            files[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
        provenance={'format':1,'transport':'stdio','requiresPython':'3.10+','requiresNode':'24+','credentialsIncluded':False,'offlineJsDependenciesIncluded':True,'files':files}
        (stage/'niio-bundle-manifest.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf8')
        with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(stage.rglob('*')):
                if p.is_file():z.write(p,'niio-skills/'+p.relative_to(stage).as_posix())
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:raise ValueError('ZIP integrity verification failed')
    result={'archive':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'bytes':output.stat().st_size,'files':len(files),'credentialsIncluded':False,'githubPublished':False}
    output.with_suffix('.sha256').write_text(result['sha256']+'  '+output.name+'\n',encoding='ascii')
    return result

if __name__=='__main__':print(json.dumps(build()))
