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