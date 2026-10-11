"""Thin F02 adapter to the proven official CLI transport; no credentials read."""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from experiments.common import dump,digest
from ..F01_response_adaptation import native as old
from ..F01_response_adaptation.phase2 import run as transport
from . import core


def preflight():
    folder=core.ROOT/'preflight';folder.mkdir(exist_ok=True)
    exe=shutil.which('codex')
    if not exe:raise RuntimeError('Codex CLI missing')
    for name,argv in [('version',['--version']),('help',['exec','--help']),('login',['login','status'])]:
        r=subprocess.run([exe,*argv],capture_output=True,timeout=30)
        (folder/(name+'_stdout.txt')).write_bytes(r.stdout);(folder/(name+'_stderr.txt')).write_bytes(r.stderr)
        if r.returncode or name=='login' and b'Logged in using ChatGPT' not in r.stdout+r.stderr:
            raise RuntimeError('Official CLI unavailable or not logged in: '+name)
    work=Path(tempfile.mkdtemp(prefix='aic_f02_probe_'))
    value=core.public(core.read(core.ROOT/'cases/C01.json'),[],'preflight_no_inference')
    raw=core.prompt(value);(work/'prompt.md').write_text(raw,encoding='utf-8')
    (work/'schema.json').write_bytes((core.ROOT/'schema.json').read_bytes())
    full=command(work,work.parent/'unused.json');configs=[]
    for i,arg in enumerate(full):
        if arg=='-c':configs+=['-c',full[i+1]]
    configs+=['-c','model='+json.dumps(core.MODEL)]
    env,removed=old.child_environment()
    r=subprocess.run([exe,*configs,'debug','prompt-input',raw],cwd=work,env=env,capture_output=True,timeout=60)
    (folder/'rendered_prompt_input.json').write_bytes(r.stdout);(folder/'render_stderr.log').write_bytes(r.stderr)
    text=r.stdout.decode('utf-8',errors='replace')
    audit={'exit_code':r.returncode,'skills_catalogs':text.count('### Available skills'),
        'SKILL_md_mentions':text.count('SKILL.md'),'OS_file_denial':False,'server_complete_context_attested':False,
        'work':str(work),'removed_environment_names':removed,'normal_product_login':True,
        'transport_setting':'model_providers.openai.supports_websockets=false',
        'official_reference':'https://learn.chatgpt.com/docs/config-file/config-reference',
        'no_auth_secret_read':True,'fresh_exec_each_turn':True}
    dump(folder/'audit.json',audit)
    if r.returncode or audit['skills_catalogs'] or audit['SKILL_md_mentions']:raise RuntimeError('Preflight config/isolation rendering failed')
    return audit


def install_command():
    # The reused function resolves this module attribute when building each invocation.
    # Set once before launching worker threads; no experiment files are modified.
    transport.native.configured_command=command


ORIGINAL_COMMAND=old.configured_command
# Avoid recursion after installing the adapter into the shared imported module.
def command(work,last):
    args=ORIGINAL_COMMAND(work,last)
    return args[:-1]+['-c','model_providers.openai.name="OpenAI"',
        '-c','model_providers.openai.requires_openai_auth=true',
        '-c','model_providers.openai.supports_websockets=false','-']


def generate(value,artifact):
    artifact=Path(artifact)
    prompt_path=core.ROOT/'prompts'/(artifact.name+'.md')
    if prompt_path.exists():raise FileExistsError('Do not regenerate a first attempt')
    prompt_path.write_text(core.prompt(value),encoding='utf-8')
    meta,output,_=transport.generate(prompt_path,core.ROOT/'schema.json',artifact,'F02_S1',None)
    checked=core.validate(output,value)
    dump(artifact/'f02_input.json',value);dump(artifact/'f02_validation.json',checked)
    dump(artifact/'f02_provenance.json',{'data_origin':value['data_origin'],'purpose':'F02_dynamic_teacher',
        'old_transport_default_origin_not_applicable':True,'same_path_history_explicitly_supplied':True,
        'public_input_sha256':digest(artifact/'f02_input.json'),'OS_file_denial':False})
    return {'output':output,'metadata':meta,'checks':checked,'artifact':str(artifact.relative_to(core.ROOT))}
