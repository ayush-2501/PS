from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

def main(inputFormat, outputFormat, summaryPatterns, examples, newInput):
    client = Anthropic()

    prompt = f"""You are an expert article summarizer. 
        Your task is to summarize a {inputFormat} into a {outputFormat} that follows the following style:
        {summaryPatterns}
        
        Here are some examples:
        {examples}  
        Here's a {outputFormat} made from a {inputFormat}, please create a {outputFormat} that follows the style above.
        {newInput}
        
        Think step-by-step about the main points of the {inputFormat} and write a {outputFormat} that follows the style and structure above. 
        Pay attention to the examples given above and try to match them as closely as possible. 
        Do not include any pre-ambles or post-ambles. Return text answer only, do not wrap answer in any XML tags."""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
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
    model: "claude-3-5-sonnet-20240620",
    max_tokens: 2048,
    temperature: 0,
    messages: [
        {"role": "user","content": prompt}
    ]
    });
    console.log(msg.content[0].text);'''

if __name__=="__main__":
    main()