module.exports = [
    {
        files: ['web/static/js/**/*.js'],
        languageOptions: {
            ecmaVersion: 2022,
            sourceType: 'module',
            globals: {
                window: 'readonly',
                document: 'readonly',
                navigator: 'readonly',
                localStorage: 'readonly',
                fetch: 'readonly',
                performance: 'readonly',
                console: 'readonly',
                confirm: 'readonly',
                setTimeout: 'readonly',
                clearTimeout: 'readonly',
                setInterval: 'readonly',
                clearInterval: 'readonly',
                URL: 'readonly',
                Blob: 'readonly',
                IntersectionObserver: 'readonly'
            }
        },
        rules: {
            'no-undef': 'error',
            'no-unused-vars': ['warn', { 'argsIgnorePattern': '^_' }],
            'no-console': 'off',
            'prefer-const': 'warn'
        }
    }
];
