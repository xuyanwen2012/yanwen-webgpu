// eslint.config.js
import js from '@eslint/js';
import htmlPlugin from 'eslint-plugin-html';

export default [
  js.configs.recommended,
  {
    files: ['**/*.{js,html}'],
    plugins: {
      html: htmlPlugin,
    },
    rules: {
      'no-unused-vars': 'warn',
    },
  },
];
