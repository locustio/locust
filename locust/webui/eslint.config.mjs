import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import typescriptEslint from '@typescript-eslint/eslint-plugin';
import prettier from 'eslint-plugin-prettier';
import unusedImports from 'eslint-plugin-unused-imports';
import _import from 'eslint-plugin-import';
import { fixupPluginRules } from '@eslint/compat';
import tsParser from '@typescript-eslint/parser';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import js from '@eslint/js';
import { FlatCompat } from '@eslint/eslintrc';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

export default [
  ...compat.extends('plugin:@typescript-eslint/recommended'),
  {
    plugins: {
      react,
      'react-hooks': fixupPluginRules(reactHooks),
      '@typescript-eslint': typescriptEslint,
      prettier,
      'unused-imports': unusedImports,
      import: fixupPluginRules(_import),
    },

    languageOptions: {
      parser: tsParser,
    },

    rules: {
      'react/display-name': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-empty-object-type': 'off',
      'no-console': 'error',
      'react/jsx-sort-props': 2,
      'react/sort-prop-types': 2,
      'import/order': [
        'error',
        {
          groups: ['external', 'internal'],
          'newlines-between': 'always',

          alphabetize: {
            order: 'asc',
            caseInsensitive: true,
          },

          pathGroups: [
            {
              pattern: 'react',
              group: 'external',
              position: 'before',
            },
            {
              pattern: 'App',
              group: 'internal',
            },
            {
              pattern: 'Report',
              group: 'internal',
            },
            {
              pattern:
                '{api,assets,components,constants,hooks,pages,redux,styles,test,types,utils}/**',
              group: 'internal',
            },
          ],

          distinctGroup: false,
          pathGroupsExcludedImportTypes: ['internal'],
        },
      ],
    },
  },
];
