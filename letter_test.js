// Test case: "ABCabcAefG"
const letters = "ABCabcAefG";
console.log("Input:", letters);

const letterData = {};
const N = letters.length;

// Process each character
for (let i = 0; i < N; i++) {
    const char = letters[i];
    const isLowercase = char >= 'a' && char <= 'z';
    const letter = char.toLowerCase();
    
    console.log(`Position ${i}: '${char}' is ${isLowercase ? 'lowercase' : 'uppercase'}`);
    
    if (!letterData[letter]) {
        letterData[letter] = {
            hasLowercase: false,
            hasUppercase: false,
            lastLowercaseIndex: -1,
            firstUppercaseIndex: N
        };
    }
    
    const data = letterData[letter];
    
    if (isLowercase) {
        data.hasLowercase = true;
        data.lastLowercaseIndex = i;
    } else {
        data.hasUppercase = true;
        if (data.firstUppercaseIndex === N) {
            data.firstUppercaseIndex = i;
        }
    }
}

console.log("\nLetter analysis:");
let count = 0;
for (const letter in letterData) {
    const data = letterData[letter];
    const isValid = data.hasLowercase && 
                   data.hasUppercase && 
                   data.lastLowercaseIndex < data.firstUppercaseIndex;
    
    console.log(`  Letter '${letter}':`);
    console.log(`    Has lowercase: ${data.hasLowercase} (last at ${data.lastLowercaseIndex})`);
    console.log(`    Has uppercase: ${data.hasUppercase} (first at ${data.firstUppercaseIndex})`);
    console.log(`    Valid: ${isValid}`);
    console.log(`    Condition: lastLower(${data.lastLowercaseIndex}) < firstUpper(${data.firstUppercaseIndex})`);
    
    if (isValid) {
        count++;
    }
}

console.log(`\nResult: ${count}`);


