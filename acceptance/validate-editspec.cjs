// Local JSON Schema validation only; never calls hap or any server.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const [validatorPath, inputPath] = process.argv.slice(2);
try {
  if (!validatorPath) throw new Error('Usage: node acceptance/validate-editspec.cjs <absolute-ajv-package-dir> [edit-spec.json]');
  const pkg = path.resolve(validatorPath);
  if (JSON.parse(fs.readFileSync(path.join(pkg, 'package.json'), 'utf8')).version !== '8.17.1') throw new Error('Expected ajv 8.17.1');
  const Ajv = require(pkg);
  const root = path.join(__dirname, '../skills/cli/niio-cli-app-editor/scripts');
  const validators = {};
  for (const directory of ['types', 'editspec']) {
    for (const name of fs.readdirSync(path.join(root, directory)).filter(n=>n.endsWith('.schema.json'))) {
      const schema = JSON.parse(fs.readFileSync(path.join(root, directory, name), 'utf8'));
      // No remote refs/loadSchema; compile against the bundled local schema only.
      validators[name] = new Ajv({strict: false, allErrors: true}).compile(schema);
    }
  }
  function validate(data) {
    if (!validators['envelope.schema.json'](data)) throw new Error('Envelope validation failed');
    for (const op of data.ops) {
      const validateOp = validators[op.type.split('.')[0] + '.schema.json'];
      if (!validateOp || !validateOp(op)) throw new Error('Operation schema validation failed');
    }
  }
  if (inputPath) validate(JSON.parse(fs.readFileSync(inputPath, 'utf8')));
  else {
    const op = {type:'field.delete', worksheet:'mock-sheet', field:'mock-field',confirm:true};
    validate({app:'mock-app',ops:[op]});
    assert.throws(()=>validate({app:'mock-app',ops:[{...op,confirm:false}]}));
    assert.throws(()=>validate({app:'mock-app',ops:[{type:'invented.op'}]}));
    assert.throws(()=>validate({app:'',ops:[]}));
  }
  console.log(JSON.stringify({schemas:Object.keys(validators).length,status:'offline-schema-passed',remoteWrites:0,
    note:'Schema acceptance does not prove server compatibility or authorize applying operations'}));
} catch (error) {
  console.error('Schema acceptance failed: ' + error.message);
  process.exitCode=1;
}
