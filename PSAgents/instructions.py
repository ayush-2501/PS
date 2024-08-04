from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import requests
import os
import time
from playwright.sync_api import sync_playwright

api_key = os.getenv("API_KEY")
cse_id = os.getenv("CSE_ID")

def fetch_url_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url, wait_until='load', timeout=120000)

            page.evaluate("""
                document.querySelectorAll('header, footer').forEach(el => el.remove());
            """)

            text = page.evaluate('document.body.innerText')
            
            cleaned_text = ' '.join(text.split())
            browser.close()
            return cleaned_text
        except Exception as e:
            browser.close()
            return f"Error fetching content from URL: {e}"

def google_search(query, api_key, cse_id, num_results=5):
    exclude_domains = ["youtube.com", "reddit.com"]
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num_results,
    }
    if exclude_domains:
        exclude_terms = " ".join(f"-site:{domain}" for domain in exclude_domains)
        params["q"] += f" {exclude_terms}"

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def llm_bot(prompt, model):
    client = OpenAI()
    if model == "gpt-4o-mini":
       response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
    elif model == "gpt-4o":
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

    return response.choices[0].message.content

def main():
    PRIMARY_KEYWORD = input("Enter Primary Keyword: ")
    SECONDARY_KEYWORDS = input("Enter Secondary Keywords: ")
    results = google_search(PRIMARY_KEYWORD, api_key, cse_id)

    search_results = []

    if results:
        for item in results.get('items', []):
            title = item['title']
            link = item['link']
            
            content = fetch_url_content(link)
            result = {
                "page_url": link,
                "page_title": title,
                "page_content": content
            }
            search_results.append(result)
        
        prompt_1 = f"""You are an expert SEO analyst tasked with analyzing the top 5 SERP (Search Engine Results Page) results for a given primary keyword. Your goal is to provide valuable insights into the content structure, themes, and search intent for each result. Follow these instructions carefully:

            1. The primary keyword for analysis is:
            <primary_keyword>
            {PRIMARY_KEYWORD}
            </primary_keyword>

            2. These are the top five search results for the primary keyword.
            <search_results>
            {search_results}
            </search_results>

            3. For each of the top 5 pages, conduct a thorough analysis following these steps:
            a. Determine the article type (e.g., listicle, how-to guide, product review, informational article, etc.)
            b. Identify common themes and structures within the content
            c. Note the search intent of the keyword based on the content (e.g., informational, transactional, navigational, commercial investigation)
            d. Count the words in each article

            4. Present your analysis for each page in the following format:
            [Insert Page Number as Page 1...]
            <page_analysis>
            <url>[Insert URL of the page]</url>
            <article_type>[Insert article type]</article_type>
            <themes_and_structure>
            - [List key themes and structural elements]
            </themes_and_structure>
            <search_intent>[Insert identified search intent]</search_intent>
            <word_count>[Insert count the words]</word_count>
            </page_analysis>

            5. After analyzing all 5 pages, provide a summary of your overall findings. Include:
            a. The most common article type
            b. Recurring themes across the top results
            c. The predominant search intent
            d. Any notable patterns or unique observations
            e. Determine Target article word count: Add the total word count across all 5 pages and divide by 5 to get the average and set the target word count that is 10-20% higher than the calculated average

            Present your summary in the following format:
            <summary>
            <common_article_type>[Insert most common article type]</common_article_type>
            <recurring_themes>
            - [List recurring themes]
            </recurring_themes>
            <predominant_intent>[Insert predominant search intent]</predominant_intent>
            <additional_observations>
            - [List any notable patterns or unique observations]
            </additional_observations>
            <target_article_word_count>[Suggest an approximate word count]</target_article_word_count>
            </summary>

            6. Ensure that your analysis is thorough, objective, and provides valuable insights for understanding the SERP landscape for the given keyword.

            Begin your analysis now, and present your findings as instructed above sequentially."""
        
        TOP_5_ARTICLES_SUMMARY = llm_bot(prompt, "gpt-4o-mini")
        print(TOP_5_ARTICLES_SUMMARY)
        
        prompt_2 = f"""You are an expert content researcher and outline creator. Your task is to analyze the summary of the top 5 articles for a given primary search query, the secondary keywords and then create an improved blog outline for a new article to rank for that search query. Follow these steps carefully:

            1. Review the primary search query:
            <primary_search_query>
            {PRIMARY_KEYWORD}
            </primary_search_query>

            2. Review the secondary keywords:
            <secondary_keywords>
            {SECONDARY_KEYWORDS}
            </secondary_keywords>

            3. Analyze the top 5 article summary:
            <top_5_articles_summary>
            {TOP_5_ARTICLES_SUMMARY}
            </top_5_articles_summary>

            4. Create an improved outline:
            - Use the common themes and structures, desired article type, search intent and target word count identified within the summary as a foundation
            - Incorporate unique elements from individual articles where relevant
            - Ensure the outline is comprehensive and improves upon the existing articles
            - Aim for a logical flow of information
            - Include an introduction and conclusion

            5. Format the outline:
            - Use <h2> tags for main headers
            - Use <h3> tags for subsections
            - Ensure proper nesting of subsections under main headers

            6. Add an FAQ section:
            - If appropriate for the topic, include an FAQ section at the end of the outline
            - Identify 3-5 common questions based on the analyzed articles (this is a great place to incorporate all the secondary keywords as well as H3 questions)
            - If an FAQ section is not appropriate, explain why

            7. Provide your final output in the following format:
            <outline>
            [Insert your formatted outline here, including H2 and H3 tags]
            </outline>

            <faq_section>
            [Insert your FAQ section or explanation for not including one]
            </faq_section>

            Remember to think critically and creatively to ensure your outline improves upon the existing articles while maintaining relevance to the search query and the search intent."""

        CONTENT_OUTLINE = llm_bot(prompt_2, "gpt-4o")
        print(CONTENT_OUTLINE)

        prompt_3 = f"""You are an expert title creator tasked with generating compelling and effective titles for content. Your goal is to create 3-5 unique title options that will grab attention, incorporate primary keywords, and appeal to the target audience. Follow these instructions carefully to produce high-quality title options.

            First, review the following inputs:

            <content_outline>
            {CONTENT_OUTLINE}
            </content_outline>

            <primary_keywords>
            {PRIMARY_KEYWORD}
            </primary_keywords>

            <target_audience>
            {TARGET_AUDIENCE}
            </target_audience>

            Now, create 3-5 title options following these guidelines:

            1. Make each title unique and compelling
            2. Include the primary keyword(s) near the beginning of each title
            3. Use power words, numbers, or questions to enhance engagement
            4. Create curiosity or promise value in each title
            5. Aim for 50-60 characters in length for each title
            6. Use proper capitalization for important words
            7. Ensure relevance and accuracy to the given topic's content outline
            8. Avoid clickbait or hyperbolic words
            9. Appeal specifically to the target audience provided

            Think carefully about how to incorporate these guidelines while crafting titles that are both attention-grabbing and relevant to the content outline and audience.

            Present your title options in the following format:

            <title_options>
            1. [First title option]
            2. [Second title option]
            3. [Third title option]
            (4. [Fourth title option])
            (5. [Fifth title option])
            </title_options>

            Remember to generate at least 3 and no more than 5 title options. Ensure that each title is unique and follows all the guidelines provided."""

        CONTENT = llm_bot(prompt_3, "gpt-4o")
        print(CONTENT)

        prompt_4 = f"""You are an expert at crafting compelling meta descriptions for web content. Your task is to create a meta description that accurately summarizes the given content, includes the primary keyword, and entices users to click through to the webpage.

            Here is the content to summarize:
            <content>
            {CONTENT}
            </content>

            The primary keyword to include in the meta description is:
            <keyword>
            {PRIMARY_KEYWORD}
            </keyword>

            To craft an effective meta description:
            1. Carefully read and understand the provided content.
            2. Identify the main topic and key points of the content.
            3. Incorporate the primary keyword naturally into your description.
            4. Summarize the content concisely, focusing on its value to the reader.
            5. Use action-oriented language to entice clicks (e.g., ""Learn how..."", ""Discover..."", ""Find out..."").
            6. Ensure your description is unique and accurately represents the content.

            Guidelines:
            - Keep the meta description between 150-160 characters long.
            - Use sentence fragments if necessary to fit key information.
            - Avoid using quotes, as they may be truncated in search results.
            - Don't simply repeat the page title or use generic descriptions.

            Please provide your crafted meta description within <meta_description> tags."""
        
        prompt_5 """You are an expert at selecting the most relevant internal product link for a blog post based on its content outline and primary keyword. Your task is to review the given information and choose the most appropriate internal link from a list of product landing pages.

            First, carefully review the following information:

            <content_outline>
            {{CONTENT_OUTLINE}}
            </content_outline>

            <primary_keyword>
            {{PRIMARY_KEYWORD}}
            </primary_keyword>

            Now, follow these steps to complete the task:

            1. Review the list of product landing pages:
            - https://productscope.ai/product-photography-backdrops/
            - https://productscope.ai/ai-fashion/
            - https://productscope.ai/background-remover/
            - https://productscope.ai/magic-erase/
            - https://productscope.ai/image-upscaler/
            - https://productscope.ai/magic-resize/
            - https://productscope.ai/magic-decompose/
            - https://productscope.ai/magic-reimagine/
            - https://productscope.ai/amazon-listing-optimization-tool/
            - https://productscope.ai/voice-of-customer-analysis/
            - https://productscope.ai/amazon-chatgpt-dobby/
            - https://productscope.ai/word-cloud-generator/
            - https://productscope.ai/magic-draw-tool/
            - https://productscope.ai/relight/
            - https://fosterfba.com/ (only linked for PPC/Ad management related keywords or topics)

            2. Analyze the content outline and primary keyword to understand the main topic and focus of the blog post.

            3. Select the most relevant product landing page that aligns with the blog post's topic. Consider the following:
            - How closely the product or service relates to the content
            - The potential value it adds to the reader
            - The natural fit within the context of the blog post

            4. If the primary keyword is related to PPC or Ad management, consider using the https://fosterfba.com/ link.

            5. Ensure that at least one product landing page is selected for internal linking.

            Provide your response in the following format:

            <product_link>
            [Insert the URL of the chosen product landing page here]
            </product_link>

            Remember, your goal is to choose the most relevant internal product link that will add value to the blog post and enhance the reader's experience."""

        prompt_6 = """You are tasked with selecting 5 to 10 additional internal links for an article based on a given content outline and primary keyword. This task is crucial for improving the website's internal linking structure and enhancing the overall SEO performance. Follow these instructions carefully:

            First, review the content outline and primary keyword provided:

            <content_outline>
            {{CONTENT_OUTLINE}}
            </content_outline>

            <primary_keyword>
            {{PRIMARY_KEYWORD}}
            </primary_keyword>

            Now, follow these steps to select the internal links:

            1. Access the sitemap by visiting this URL: https://productscope.ai/post-sitemap.xml

            2. Carefully review the sitemap and identify 5-10 blog pages that are closely related to the main topic outlined in the content outline and primary keyword. Consider the following criteria:
            - Relevance to the main topic
            - Complementary information that enhances the reader's understanding
            - Posts that cover subtopics mentioned in the content outline

            3. For each selected post, choose an appropriate anchor text. The anchor text should:
            - Ideally be the main keyword of the linked post
            - Be natural and contextually relevant to both the source and target content
            - Accurately describe the content of the linked page

            4. Note down the URL and chosen anchor text for each selected post.

            5. Present your selections in the following format:
            <internal_links>
            1. Anchor text: [Insert chosen anchor text]
                URL: [Insert full URL of the selected post]

            2. Anchor text: [Insert chosen anchor text]
                URL: [Insert full URL of the selected post]

            [Continue for all selected links]
            </internal_links>

            6. After making your selections, double-check that:
            - All selected posts are relevant to the main topic
            - There are no duplicate links
            - You have selected between 5 to 10 links

            Remember, the goal is to enhance the article's value and improve internal linking, so choose links that genuinely complement the content outlined in the provided structure."""
        
        prompt_7 = """You will be creating a compelling introduction for a blog post using the PAS (Problem-Agitate-Solution) Framework. Here's the content outline and title options for the blog post:

            <content_outline>
            {{CONTENT_OUTLINE}}
            </content_outline>

            <title_options>
            {{TITLE_OPTIONS}}
            </title_options>

            The PAS Framework consists of three elements:
            1. Problem: Identify a problem or pain point that your target audience is experiencing.
            2. Agitate: Emphasize the negative consequences of not addressing this problem.
            3. Solution: Present your solution or approach to solving the problem.

            To create the introduction:
            1. Review the content outline and title options to understand the main topic and target audience.
            2. Identify the core problem or pain point addressed in the blog post.
            3. Write a brief, attention-grabbing opening sentence that highlights this problem.
            4. Agitate the problem by describing its negative impacts or potential consequences.
            5. Hint at the solution your blog post will provide, creating anticipation for the reader.

            Your introduction should be concise and engaging, limited to 100 words. Write your introduction inside <introduction> tags.

            Remember to maintain a tone that matches the blog post's intended style and audience."""
        
        prompt_8 = """You are an expert content writer tasked with creating high-quality, original content based on the provided information. Your goal is to produce an article that is informative, engaging, and optimized for search engines while maintaining a natural, conversational tone.

            Here's the content outline you'll be working with:
            <content_outline>
            {{CONTENT_OUTLINE}}
            </content_outline>

            Choose the most appropriate title from the following options:
            <title_options>
            {{TITLE_OPTIONS}}
            </title_options>

            Select the title that best captures the essence of the content and incorporates the primary keyword naturally. Place your chosen title at the beginning of your article.

            The primary keyword for this article is:
            <primary_keyword>{{PRIMARY_KEYWORD}}</primary_keyword>

            Incorporate this keyword naturally throughout the content, especially in the introduction and conclusion.

            Here are the secondary keywords to include:
            <secondary_keywords>
            {{SECONDARY_KEYWORDS}}
            </secondary_keywords>

            Integrate these secondary keywords throughout the article where they fit naturally and add value to the content.

            Here's the introduction you will be using in this article:
            <introduction>
            {{INTRODUCTION}}
            </introduction>


            You should include the following product link in your content:
            <product_link>{{PRODUCT_LINK}}</product_link>

            Incorporate this link naturally within the content where it's most relevant and valuable to the reader.

            The meta description for this article is:
            <meta_description>{{META_DESCRIPTION}}</meta_description>

            Use this as a guide for the overall focus and tone of your article.

            The desired word count for this article is:
            <word_count>{{DESIRED_WORD_COUNT}}</word_count>

            Now, follow these steps to write the content:

            1. Start with a compelling introduction that incorporates the primary keyword and sets the tone for the article.
            2. Follow the content outline provided, expanding on each point in detail.
            3. Use a conversational tone and style throughout the article.
            4. Provide actionable insights and practical advice where possible.
            5. Naturally incorporate the product link where they add value to the content.
            6. Use all the secondary keywords atleast once throughout the article in a natural, non-forced manner.
            7. Conclude with a strong summary that reinforces the main points and includes a call-to-action if appropriate.
            8. Proofread your content for grammar and spelling errors.

            Throughout the writing process, keep in mind Google's E-E-A-T (Experience, Expertise, Authoritativeness, and Trustworthiness) framework. Demonstrate your expertise on the topic, provide accurate and up-to-date information, and cite reputable sources where necessary.

            Ensure that your final article strictly adheres to the desired word count.

            Present your completed article within <article> tags."""
        
        prompt_9 = """You are an expert SEO optimizer. Your task is to optimize an article for search engines while maintaining readability and user experience. You will be provided with an article, a primary keyword, secondary keywords, and internal links. Follow these steps to optimize the article:

            1. Review the following inputs:

            <article>
            {{ARTICLE}}
            </article>

            <primary_keyword>{{PRIMARY_KEYWORD}}</primary_keyword>

            <secondary_keywords>
            {{SECONDARY_KEYWORDS}}
            </secondary_keywords>

            <internal_links>
            {{INTERNAL_LINKS}}
            </internal_links>

            2. Analyze the article and keywords:
            - Read through the article carefully
            - Understand the main topic and structure of the article
            - Identify opportunities to naturally integrate the primary and secondary keywords
            - Look for appropriate places to add internal and external links

            3. Optimize the article following these guidelines:

            a. Keyword integration:
                - Naturally include the primary keyword and secondary keywords throughout the article
                - Avoid keyword stuffing; prioritize readability and user experience
                - Aim for a keyword density of 1-2% for the primary keyword

            b. Title tag optimization:
                - Ensure the title tag (H1) includes the primary keyword
                - Keep the title tag under 60 characters if possible

            c. Header structure:
                - Use H1 for the main title (only one H1 per article)
                - Use H2 for main sections
                - Use H3 for subsections
                - Include keywords in headers where it makes sense naturally

            d. Internal linking:
                - Add all the provided internal links naturally where relevant
                - Use appropriate anchor text for each link, preferably including target keywords

            e. External linking:
                - Add 1-2 high-quality external links to non-competing, authoritative resources
                - Ensure external links are relevant to the content

            4. Provide your optimized version of the article in the following format:

            <optimized_article>
            [Insert the full optimized article here, including all headers, paragraphs, and links]
            </optimized_article>

            Remember to always prioritize readability and user experience over keyword density. The optimized article should flow naturally and provide value to the reader while also being optimized for search engines."""

    else:
        print("Error performing search")

if __name__=="__main__":
    main()
