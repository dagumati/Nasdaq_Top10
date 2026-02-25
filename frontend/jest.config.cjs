// Jest configuration
module.exports = {
    testEnvironment: 'jsdom',
    transform: {
        '^.+\\.(js|jsx)$': 'babel-jest',
    },
    moduleNameMapper: {
        '\\.(css|less|scss)$': '<rootDir>/__mocks__/styleMock.js',
    },
    setupFilesAfterFramework: ['@testing-library/jest-dom'],
    testMatch: ['**/__tests__/**/*.{js,jsx}', '**/*.test.{js,jsx}'],
}
