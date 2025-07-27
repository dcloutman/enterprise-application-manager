module.exports = {
	root: true,
	extends: [
		'eslint:recommended',
		'@typescript-eslint/recommended',
		'prettier'
	],
	parser: '@typescript-eslint/parser',
	plugins: ['@typescript-eslint'],
	parserOptions: {
		sourceType: 'module',
		ecmaVersion: 2020,
		extraFileExtensions: ['.svelte']
	},
	env: {
		browser: true,
		es2017: true,
		node: true
	},
	overrides: [
		{
			files: ['*.svelte'],
			processor: 'svelte3/svelte3',
			plugins: ['svelte3'],
			rules: {
				'@typescript-eslint/no-unused-vars': 'off'
			}
		},
		{
			files: ['**/*.test.ts', '**/*.spec.ts'],
			env: {
				vitest: true
			},
			rules: {
				'@typescript-eslint/no-explicit-any': 'off'
			}
		}
	],
	rules: {
		'@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
		'@typescript-eslint/no-explicit-any': 'warn',
		'no-console': 'warn'
	}
};
