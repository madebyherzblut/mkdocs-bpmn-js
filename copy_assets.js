const fs = require('fs-extra');
const path = require('path');

const bpmnJsPath = path.dirname(require.resolve('bpmn-js/package.json'));
const sourceDir = path.join(bpmnJsPath, 'dist');
const assetsDir = path.join(sourceDir, 'assets');
const targetDir = path.join(__dirname, 'src', 'mkdocs_bpmn_js', 'assets');

// Files to copy from the root of the dist directory
const filesToCopy = [
  'bpmn-navigated-viewer.production.min.js',
];

// Files to copy from the assets directory
const assetFilesToCopy = [
    'bpmn-js.css'
];

async function copyAssets() {
  try {
    // Ensure the target directory exists
    await fs.ensureDir(targetDir);

    // Copy files from the root of the dist directory
    for (const file of filesToCopy) {
      const sourceFile = path.join(sourceDir, file);
      const targetFile = path.join(targetDir, file);
      await fs.copy(sourceFile, targetFile);
      console.log(`Copied ${file} to ${targetDir}`);
    }

    // Copy files from the assets directory
    for (const file of assetFilesToCopy) {
        const sourceFile = path.join(assetsDir, file);
        const targetFile = path.join(targetDir, file);
        await fs.copy(sourceFile, targetFile);
        console.log(`Copied ${file} to ${targetDir}`);
    }

    console.log('Asset copying completed successfully.');
  } catch (err) {
    console.error('Error copying assets:', err);
    process.exit(1);
  }
}

copyAssets();