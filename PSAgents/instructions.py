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

def llm_bot(prompt):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def main():
    PRIMARY_KEYWORD = input("Enter Primary Keyword: ")
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

        '''for result in search_results:
            print(f"URL: {result['page_url']}")
            print(f"Title: {result['page_title']}")
            print(f"Content: {result['page_content'][:200]}...")
            print()'''
        
        prompt = f"""You are an expert SEO analyst tasked with analyzing the top 5 SERP (Search Engine Results Page) results for a given primary keyword. Your goal is to provide valuable insights into the content structure, themes, and search intent for each result. Follow these instructions carefully:

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
        
        response = llm_bot(prompt)
        print(response)

    else:
        print("Error performing search")

if __name__=="__main__":
    main()
