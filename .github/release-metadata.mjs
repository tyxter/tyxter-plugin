import { appendFileSync, readFileSync } from 'node:fs';

const readManifest = (path) => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'));
const claude = readManifest('../.claude-plugin/plugin.json');
const codex = readManifest('../.codex-plugin/plugin.json');
const { version } = claude;
const numeric = '(0|[1-9][0-9]*)';
const identifier = '(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)';
const semver = new RegExp(
  `^${numeric}\\.${numeric}\\.${numeric}(?:-${identifier}(?:\\.${identifier})*)?(?:\\+[0-9A-Za-z-]+(?:\\.[0-9A-Za-z-]+)*)?$`,
);
if (typeof version !== 'string' || !semver.test(version)) {
  throw new Error('Claude manifest must contain a valid SemVer version');
}
if (codex.version !== version || codex.name !== claude.name) {
  throw new Error('Claude and Codex manifests must have matching names and versions');
}
const ref = process.env.GITHUB_REF ?? '';
if (ref.startsWith('refs/tags/') && ref !== `refs/tags/v${version}`) {
  throw new Error('Release tag must match v<plugin manifest version>');
}
const stable = ref === `refs/tags/v${version}` && /^\d+\.\d+\.\d+$/.test(version);
const output = `stable=${stable}\n`;
if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, output);
process.stdout.write(output);
