from extract_pattern import main as ep  
from main_agent import main as mg  

def main():
    
    # Initialize agent 
    inputFormat = input()
    outputFormat = input()
    
    # Examples for Pattern Extraction
    USER_INPUT_FORMAT = input("Enter example input ")
    DESIRED_OUTPUT_FORMAT = input("Enter example output ")
    summaryPatterns = ep(USER_INPUT_FORMAT, DESIRED_OUTPUT_FORMAT)

    examples = "User Input example:\n" + USER_INPUT_FORMAT + "\nUser Output example:\n" + DESIRED_OUTPUT_FORMAT
    newInput = input("Enter your input ")
    result = mg(inputFormat, outputFormat, summaryPatterns, examples, newInput)

    print(result)

if __name__=="__main__":
    main()

'''
// Mock implementation of extract_pattern and main_agent
// Replace these with actual implementations
function extractPattern(inputFormat, outputFormat) {
    // Implement pattern extraction logic
    return `Extracted patterns from ${inputFormat} to ${outputFormat}`;
}

function mainAgent(inputFormat, outputFormat, summaryPatterns, examples, newInput) {
    // Implement main agent logic
    return `Processed input ${newInput} with patterns ${summaryPatterns}`;
}

// Main function
function main() {
    const readline = require('readline');

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    rl.question('Enter input format: ', (inputFormat) => {
        rl.question('Enter output format: ', (outputFormat) => {
            rl.question('Enter example input: ', (userInputExample) => {
                rl.question('Enter example output: ', (desiredOutputExample) => {
                    const summaryPatterns = extractPattern(userInputExample, desiredOutputExample);

                    const examples = `User Input example:\n${userInputExample}\nUser Output example:\n${desiredOutputExample}`;
                    rl.question('Enter your input: ', (newInput) => {
                        const result = mainAgent(inputFormat, outputFormat, summaryPatterns, examples, newInput);
                        console.log(result);
                        rl.close();
                    });
                });
            });
        });
    });
}

main();
'''