/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        '**/*.html'
    ],
    theme: {
        extend: {
            fontFamily: {},
            color: {
                primary: 'var(--primary-color)',
                secondary: 'var(--secondary-color)',
            },
        },
    },
    plugins: [],
}

