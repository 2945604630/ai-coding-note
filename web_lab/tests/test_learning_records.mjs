import test from 'node:test';
import assert from 'node:assert/strict';
import { jobsForVersion, executionSummary, collectMistakes, isPracticeRecord } from '../static/learning-records.js';

const v1={version_id:'old',source_sha256:'a',source:'old'};
const v2={version_id:'new',source_sha256:'b',source:'new'};
const e={experiment_id:'session',session_id:'session',feature:'DEMO',case_id:'C01',source_type:'real_user',code_versions:[v1,v2],current_code_version_id:'new',demo:{operations:[]},sandbox:{jobs:[]}};
const job=(overrides={})=>({session_id:'session',task_id:'job',version_id:'old',source_sha256:'a',status:'failed',mode:'submit',executed:true,created_at:'2026-10-12T01:00:00Z',results:[{input:3,status:'failed',executed:true,cleaned:true,stdout:'3\n',expected_output:'6\n'}],...overrides});
test('old success and mismatched hash cannot become new-version results',()=>{
  e.sandbox.jobs=[job({status:'passed'}),job({version_id:'new',source_sha256:'wrong'}),job({session_id:'other',version_id:'new',source_sha256:'b'})];
  assert.deepEqual(jobsForVersion(e,v2),[]);
  assert.equal(executionSummary(e,v2).kind,'unrun');
});
test('a custom run without reference never gets a passed-test label',()=>{
  e.sandbox.jobs=[job({version_id:'new',source_sha256:'b',status:'completed',mode:'run',results:[{input:8,status:'completed',executed:true,cleaned:true,stdout:'36\n',expected_output:null}]})];
  assert.equal(executionSummary(e,v2).kind,'completed');
});
test('failure records retain exact version and do not admit fabricated execution',()=>{
  e.sandbox.jobs=[job(),job({task_id:'fake',status:'completed',executed:false,results:[]}),job({task_id:'foreign',session_id:'other'}),job({task_id:'wrong',source_sha256:'wrong'})];
  const mistakes=collectMistakes([e]);
  assert.equal(mistakes.length,1);assert.equal(mistakes[0].version.version_id,'old');assert.equal(mistakes[0].job.task_id,'job');
});
test('automated fixtures are explicit and excluded from student record views',()=>{
  assert.equal(isPracticeRecord({...e,creation_input_origin:{kind:'automated_test'}}),false);
  assert.equal(isPracticeRecord(e),true);
});
