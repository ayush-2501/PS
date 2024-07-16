from extract_pattern import main as ep  
from main_agent import main as mg  

def main():
    
    inputFormat = input()
    inputFormat = "Feature Headline"
    
    outputFormat = input()
    outputFormat = "Tweet"
    
    USER_INPUT_FORMAT = input("Enter example input ")
    USER_INPUT_FORMAT = "New magic edit tool: Magic Resize that can resize product photos into multiple resolutions and aspect ratios using AI in seconds."
    
    DESIRED_OUTPUT_FORMAT = input("Enter example output ")
    DESIRED_OUTPUT_FORMAT = """🔮 Expand Product Photos with Magic Resize ✨

        Easily transform your non-square photos into perfect squares.
        AI seamlessly extends your image naturally in seconds.

        Say goodbye to awkward empty spaces.

        Experience the magic now → ProductScope.AI ✨
        """
    
    summaryPatterns = ep(USER_INPUT_FORMAT, DESIRED_OUTPUT_FORMAT)

    examples = "User Input example:\n" + USER_INPUT_FORMAT + "\nUser Output example:\n" + DESIRED_OUTPUT_FORMAT

    newInput = input("Enter your input ")
    #newInput = "Rolled out a new tool called AI Fashion where users can simply upload their garment and use AI to try it on any model in any custom setting of their choice"

    result = mg(inputFormat, outputFormat, summaryPatterns, examples, newInput)

    print(result)

if __name__=="__main__":
    main()