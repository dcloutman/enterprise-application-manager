module.exports = {
	plugins: ['prettier-plugin-svelte'],
	pluginSearchDirs: ['.'],
	overrides: [
		{
			files: '*.svelte',
			options: {
				parser: 'svelte'
			}
		}
	],
	semi: true,
	singleQuote: true,
	tabWidth: 2,
	useTabs: true,
	trailingComma: 'none',
	printWidth: 100,
	bracketSpacing: true,
	arrowParens: 'avoid',
	endOfLine: 'lf'
};
