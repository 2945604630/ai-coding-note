import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const source = await readFile(new URL('../static/learning-state.js', import.meta.url), 'utf8').catch(() => '');
const state = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
assert.equal(typeof state.needsReview, 'function', 'real output mismatches must be reviewable');
assert.equal(state.needsReview({status:'completed', results:[{stdout:'3\n', expected_output:'6\n'}]}), true);
assert.equal(state.needsReview({status:'completed', results:[{stdout:'36\n', expected_output:null}]}), false);
assert.equal(state.needsReview({status:'passed', results:[]}), false);
assert.equal(state.needsReview({status:'passed', results:[{stdout:'6\r\n',expected_output:'6\n'}]}), false,
    'CRLF judged as passed by the backend must not become an error in review');
assert.equal(state.needsReview({status:'timeout', results:[]}), true);
const version={version_id:'new', source_sha256:'abc'};
assert.equal(state.currentJob([{version_id:'old',source_sha256:'abc',status:'passed'}],version), null,
    'same text in another version is still historical evidence');
assert.equal(state.currentJob([{version_id:'new',source_sha256:'abc',status:'passed'},
    {version_id:'new',source_sha256:'abc',status:'running'}],version).status,'running',
    'pending latest task must not fall back to older passing task');
assert.equal(state.coachGate({dirty:true,historical:false,busy:false}), '先保存编辑，再发送给教练。');
assert.equal(state.coachGate({dirty:false,historical:true,busy:false}), '请回到当前保存版本后再发送。');
assert.equal(state.coachGate({dirty:false,historical:false,busy:true}), '等待运行结束后再发送，教练才能看到这次结果。');
assert.equal(state.coachGate({dirty:false,historical:false,busy:false}), '');
assert.equal(typeof state.retryGate, 'function', 'retry must respect draft, view and execution snapshot boundaries');
assert.equal(state.retryGate({dirty:true,historical:false,busy:false,turnVersion:'v1',currentVersion:'v1'}), '先保存编辑，再发送给教练。');
assert.equal(state.retryGate({dirty:false,historical:false,busy:false,turnVersion:'v1',currentVersion:'v2'}), '这次调用使用旧版本。请开始新的辅导，原失败记录会保留。');
assert.equal(state.retryGate({dirty:false,historical:true,busy:false,turnVersion:'v1',currentVersion:'v1'}), '请回到当前保存版本后再发送。');
assert.equal(state.retryGate({dirty:false,historical:false,busy:true,turnVersion:'v1',currentVersion:'v1'}), '等待运行结束后再发送，教练才能看到这次结果。');
assert.equal(state.retryGate({dirty:false,historical:false,busy:false,turnVersion:'v1',currentVersion:'v1'}), '');
console.log('V3 state regression passed: output comparison, version identity, latest task, send and retry boundaries');
