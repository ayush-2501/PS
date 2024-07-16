from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

def main(USER_INPUT_FORMAT, DESIRED_OUTPUT_FORMAT):
    client = Anthropic()

    prompt = f"""You are tasked with extracting the pattern to match the voice, tone, style, and structure of a given output format based on a user input format. Your goal is to identify the key elements that transform the input into the desired output.

        First, carefully examine the user input format:
        
        <user_input_format>
        {USER_INPUT_FORMAT}
        </user_input_format>

        Now, analyze the desired output format:
        
        <desired_output_format>
        {DESIRED_OUTPUT_FORMAT}
        </desired_output_format>

        To extract the pattern, follow these steps:
        1. Compare the input and output formats, noting the differences in structure, language, and presentation.
        2. Identify specific elements of tone, voice, personality, style, and structure that are present in the output but not in the input.
        3. Look for recurring patterns or techniques used in the output format.
        4. Consider how the information from the input is transformed or enhanced in the output.

        When extracting the pattern:
        - Be specific and detailed in your observations.
        - Use bullet points for each aspect within the categories.
        - Focus on elements that are consistently present in the output format.
        - Include any unique or distinctive features of the output format.
        - If certain elements are not clearly defined by the given formats, you may omit that category or note it as "Not clearly defined in the given formats.

        Based on your analysis, provide a detailed breakdown of the pattern in the following format:
        Tone:
        - [List key aspects of the tone]

        Voice:
        - [List key aspects of the voice]

        Personality:
        - [List key aspects of the personality]

        Style:
        - [List key aspects of the style]

        Structure:
        - [List key aspects of the structure]

        Additional notes:
        - [Include any other relevant observations or patterns]"""
    
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=2048,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text

    '''import Anthropic from "@anthropic-ai/sdk";

    const anthropic = new Anthropic();

    const msg = await anthropic.messages.create({
    model: "claude-3-haiku-20240307",
    max_tokens: 2048,
    temperature: 0,
    messages: [
        {"role": "user","content": prompt}
    ]
    });
    console.log(msg.content[0].text);'''

if __name__=="__main__":
    main()