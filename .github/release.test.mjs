import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';

test('release channels require matching manifests and an exact SemVer tag', () => {
  const root = mkdtempSync(join(tmpdir(), 'tyxter-plugin-release-'));
  try {
    for (const dir of ['.github', '.claude-plugin', '.codex-plugin']) {
      mkdirSync(join(root, dir));
    }
    const script = join(root, '.github/release-metadata.mjs');
    copyFileSync(new URL('./release-metadata.mjs', import.meta.url), script);
    const run = (version, ref, codexVersion = version, codexName = 'tyxter') => {
      writeFileSync(
        join(root, '.claude-plugin/plugin.json'),
        JSON.stringify({ name: 'tyxter', version }),
      );
      writeFileSync(
        join(root, '.codex-plugin/plugin.json'),
        JSON.stringify({ name: codexName, version: codexVersion }),
      );
      return spawnSync(process.execPath, [script], {
        encoding: 'utf8',
        env: {
          PATH: process.env.PATH,
          GITHUB_REF: ref,
          GITHUB_OUTPUT: join(root, 'output'),
        },
      });
    };
    for (const [version, ref, stable] of [
      ['1.2.3', 'refs/tags/v1.2.3', true],
      ['1.2.3', 'refs/heads/main', false],
      ['1.2.3-rc.1', 'refs/tags/v1.2.3-rc.1', false],
      ['1.2.3+build.1', 'refs/tags/v1.2.3+build.1', false],
    ]) {
      const result = run(version, ref);
      assert.equal(result.status, 0, result.stderr);
      assert.equal(result.stdout, `stable=${stable}\n`);
    }
    assert.match(readFileSync(join(root, 'output'), 'utf8'), /stable=true\nstable=false/);
    for (const [version, ref, codexVersion, codexName] of [
      ['1.2.3', 'refs/tags/v1.2.4'],
      ['1.2.3', 'refs/tags/v1.2.3', '1.2.4'],
      ['1.2.3', 'refs/tags/v1.2.3', '1.2.3', 'other'],
      ['01.2.3', 'refs/tags/v01.2.3'],
      ['1.2.3-01', 'refs/tags/v1.2.3-01'],
      ['1.2', 'refs/tags/v1.2'],
      [null, 'refs/heads/main'],
    ]) {
      assert.notEqual(run(version, ref, codexVersion, codexName).status, 0);
    }
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
