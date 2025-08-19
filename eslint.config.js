// eslint.config.mjs
import js from '@eslint/js';
import html from 'eslint-plugin-html';
import globals from 'globals';

export default [
  js.configs.recommended,

  // Lint inline <script> inside .html files too
  {
    files: ['**/*.{js,html}'],
    plugins: {html},
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        // Browser built-ins (document, navigator, performance, console, etc.)
        ...globals.browser,

        // WebGPU enums & types exposed on the global object
        GPUBufferUsage: 'readonly',
        GPUMapMode: 'readonly',
        GPUShaderStage: 'readonly',
        GPUTextureUsage: 'readonly',
        GPUAddressMode: 'readonly',
        GPUCompareFunction: 'readonly',
        GPUFilterMode: 'readonly',
        GPU: 'readonly',
        GPUCanvasContext: 'readonly',
      },
    },
    rules: {
      // keep this on; the globals above make it happy
      'no-undef': 'error',
    },
  },
];