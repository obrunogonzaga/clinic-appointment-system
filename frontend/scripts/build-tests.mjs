import { buildSync } from 'esbuild';
import { mkdirSync, readdirSync, rmSync, statSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');
const testsRoot = join(projectRoot, 'src', 'tests');
const distDir = join(projectRoot, 'dist-tests');

const collectTests = (directory) => {
  const entries = readdirSync(directory);
  const files = [];

  for (const entry of entries) {
    const fullPath = join(directory, entry);
    const stats = statSync(fullPath);

    if (stats.isDirectory()) {
      files.push(...collectTests(fullPath));
    } else if (entry.endsWith('.test.ts') || entry.endsWith('.test.tsx')) {
      files.push(fullPath);
    }
  }

  return files;
};

const entryPoints = collectTests(testsRoot);

if (entryPoints.length === 0) {
  console.warn('Nenhum teste encontrado.');
  process.exit(0);
}

rmSync(distDir, { recursive: true, force: true });
mkdirSync(distDir, { recursive: true });

buildSync({
  entryPoints,
  outdir: distDir,
  bundle: true,
  platform: 'node',
  format: 'cjs',
  logLevel: 'error',
  jsx: 'automatic',
  sourcemap: false,
  outbase: testsRoot,
  outExtension: { '.js': '.cjs' },
});

const relativeEntries = entryPoints.map((entry) => relative(testsRoot, entry));
console.info(`Testes compilados: ${relativeEntries.join(', ')}`);
