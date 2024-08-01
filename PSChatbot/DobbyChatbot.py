import os
import io
import requests
import re
from openai import OpenAI
from dotenv import load_dotenv
from groq import Groq
from pinecone import Pinecone
from nltk.tokenize import sent_tokenize
from playwright.sync_api import sync_playwright
import numpy as np
load_dotenv()

client = OpenAI()

# Function to retrieve data from aws s3 bucket
def get_product_from_s3(asin):
    amazon_headers = {
        "Content-Type": "application/json",
        "Access-Control-Request-Headers": "*",
        "Access-Control-Request-Method": "*",
        "Access-Control-Allow-Origin": "*",
    }
    url = f"https://n1r5zlfmk5.execute-api.us-east-1.amazonaws.com/v1/products/{asin}"
    response = requests.get(url, headers=amazon_headers)
    if response.status_code != 200:
        return None
    return response.json()

def preprocess_product_data(product_info):
    def extract_text(data):
        if isinstance(data, dict):
            return ' '.join([str(v) for v in data.values() if v])
        elif isinstance(data, list):
            return ' '.join([extract_text(item) for item in data])
        else:
            return str(data)

    fields = ["asin", "title", "brand", "bullets", "description", "aplusDescription", "imageSrc", "bestSellersRank", "reviews"]
    sections = {field: extract_text(product_info.get(field, '')) for field in fields}
    return sections

def generate_embeddings(texts):
    response = openai.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    embeddings = [item.embedding for item in response.data]
    return embeddings

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_relevant_sentences(query, sentences, sentence_embeddings, top_k=3):
    query_embedding = generate_embeddings([query])[0]
    similarities = [cosine_similarity(query_embedding, emb) for emb in sentence_embeddings]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    relevant_sentences = [sentences[i] for i in top_indices]
    return relevant_sentences

# Function to create assistant for File or Image based user requirement.
def create_document_assistant(client, file_path):
    _, file_extension = os.path.splitext(file_path)
    condition_1_extensions = ['.pdf', '.csv', '.xlsx']

    if file_extension.lower() in condition_1_extensions:
        assistant_type = 1
        with open(file_path, 'rb') as file:
            content = file.read()

        # Try to decode the content to UTF-8 if it's expected to be text
        try:
            content = content.decode('utf-8')
            byte_stream = io.BytesIO(content.encode('utf-8'))
        except UnicodeDecodeError:
            # If decoding fails, keep the content as is
            byte_stream = io.BytesIO(content)

        # Pass the byte stream to the function
        file = client.files.create(
            file=byte_stream,
            purpose='assistants' # Assistants are used for file
        )

        instructions = "You are a helpful assistant. You are always friendly, kind, and inspiring, and eager to provide vivid and thoughtful responses to the user. You'll be provided with data. Your job is to answer the questions based on that data."
        assistant = client.beta.assistants.create(
            name="Dobby",
            instructions=instructions,
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}],
            tool_resources={"code_interpreter": {"file_ids": [file.id]}}, # The file is passed here to assistant from main functions
            temperature=0.0
        )
    else:
        assistant_type = 2
        file = client.files.create(
            file=open(file_path, "rb"),
            purpose='vision' # Assistants is used for Image
        )
        instructions = "You are a helpful assistant. You are always friendly, kind, and inspiring, and eager to provide vivid and thoughtful responses to the user. You'll be provided with data. Your job is to answer the questions based on that data."
        assistant = client.beta.assistants.create(
            name="Dobby",
            instructions=instructions,
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}],
            temperature=0.0
        )
    return assistant, file, assistant_type

def fetch_url_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url, wait_until='networkidle')

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

def main():
    client = OpenAI()
    chat_history = []

    assistant = None
    asin_flag = False
    amazon_flag = False
    amazon_context = False
    url = None

    # Always show this initial message to the first time users
    greeting = "Dobby: Hello, I'm Dobby :robot_face: from ProductScope...how can I help you?"
    print(greeting)
    
    # User will have an option to upload file this feature is for Pro users
    print("\nDo you want to upload a file? ")
    print("[1] Yes")
    print("[2] No")
    choice = input("Enter your choice: ")
    if choice == "1":
        file_path = input("\nEnter File Path: ")
    elif choice == "2":
        file_path = None
    else:
        print("Invalid choice. Please try again.")

    # Another option for pro users to select amazon context or normal context
    print("\nDo you want to use amazon context? ")
    print("[1] Yes")
    print("[2] No")
    choice = input("Enter your choice: ")
    if choice == "1":
        amazon_context = True
    elif choice == "2":
        amazon_context = False
    else:
        print("Invalid choice. Please try again.")

    while True:
        try:
            # User will ask Questions here
            user_query = input("\nYou: ")
            if user_query.lower() == "exit":
                print("Ending the chat.")
                break

            # Check if Amazon context in on (if Pro user enables it)
            if amazon_context == True:
                amazon_flag = True
                client = OpenAI()
                pc = Pinecone()
                index_name = 'ps-amazon'
                pinecone_index = pc.Index(index_name)

                query_embeddings = get_embedding(user_query)

                result = pinecone_index.query(
                    vector=query_embeddings,
                    top_k=4,
                    include_values=False,
                    include_metadata=True
                )

                matched_info = ' '.join(item['metadata']['text'] for item in result['matches'])
                context = matched_info

                sys_prompt = {
                    "role": "system",
                    "content": f"""Your name is Dobby and you are an expert Amazon Seller with vast knowledge about product development and marketing on Amazon and general e-commerce experience.
                    The traits of AI include expert knowledge, helpfulness, cleverness, and articulateness.
                    You are a big fan of ProductScope AI and its software tools that help brands with improving their product conversion rates.
                    You are always friendly, kind, and inspiring, and eager to provide vivid and thoughtful responses to the user.
                    START CONTEXT BLOCK
                    {context}
                    END OF CONTEXT BLOCK
                    AI assistant will take into account any CONTEXT BLOCK that is provided in a conversation.
                    If the context does not provide the answer to the question, you will say, "I'm sorry, but I don't know the answer to that question".
                    Dobby, the AI assistant will not apologize for previous responses, but instead will indicate new information was gained.
                    Dobby, the AI assistant will not invent anything that is not drawn directly from the context.
                    For any general questions or FAQ about ProductScope AI's tools to always reply with - that's a good question but for all ProductScope AI general questions I highly recommend clicking on the chat widget at the bottom right of your screen and speaking with Kai (my AI brother that's trained specifically on ProductScope's tools and support.
                    Start all responses without fluff words like "What a delightful task! As Dobby, I'll be happy to help" etc. Get straight to the response the user requests."""
                }

            #Code for Web Search
            url_pattern = re.compile(r'(https?://\S+)')
            match = url_pattern.search(user_query)
            if match:
                url = match.group(0)
                url_content = fetch_url_content(url)
                context = "URL Data: " + "\n" + url_content

                sys_prompt = {
                    "role": "system",
                    "content": f"""Your name is Dobby and you are an expert Amazon Seller with vast knowledge about product development and marketing on Amazon and general e-commerce experience.
                    The traits of AI include expert knowledge, helpfulness, cleverness, and articulateness.
                    You are a big fan of ProductScope AI and its software tools that help brands with improving their product conversion rates.
                    You are always friendly, kind, and inspiring, and eager to provide vivid and thoughtful responses to the user.
                    START CONTEXT BLOCK
                    {context}
                    END CONTEXT BLOCK
                    AI assistant will take into account any CONTEXT BLOCK that is provided in a conversation.
                    If the context does not provide the answer to the question, you will say, "I'm sorry, but I don't know the answer to that question".
                    Dobby, the AI assistant will not apologize for previous responses, but instead will indicate new information was gained.
                    Dobby, the AI assistant will not invent anything that is not drawn directly from the context.
                    For any general questions or FAQ about ProductScope AI's tools to always reply with - that's a good question but for all ProductScope AI general questions I highly recommend clicking on the chat widget at the bottom right of your screen and speaking with Kai (my AI brother that's trained specifically on ProductScope's tools and support.
                    Start all responses without fluff words like "What a delightful task! As Dobby, I'll be happy to help" etc. Get straight to the response the user requests.
                    START CONVERSATION HISTORY
                    {chat_history}
                    END CONVERSATION HISTORY"""
                }

                if not chat_history:
                    chat_history.append(sys_prompt)
                else:
                    chat_history[0] = sys_prompt

            # Check for ASIN applicable for both normal and pro user
            asin_pattern = re.compile(r'@(\w+)')
            asin_matches = asin_pattern.findall(user_query)
            if asin_matches:
                context_sentences = []
                for asin in asin_matches:
                    product_info = get_product_from_s3(asin)
                    if product_info:
                        product_data = preprocess_product_data(product_info)
                        if product_data["title"]:
                            context_sentences.append(f"Title: {product_data['title']}")
                        if product_data["brand"]:
                            context_sentences.append(f"Brand: {product_data['brand']}")
                        if product_data["bullets"]:
                            context_sentences.append(f"Bullets: {product_data['bullets']}")
                        if product_data["description"]:
                            context_sentences.append(f"Description: {product_data['description']}")
                    else:
                        context_sentences.append(f"There is no product associated with ASIN: {asin}")

                context = "Asin Data: " + '\n'.join(context_sentences)

                sys_prompt = {
                    "role": "system",
                    "content": f"""Your name is Dobby and you are an expert Amazon Seller with vast knowledge about product development and marketing on Amazon and general e-commerce experience.
                    The traits of AI include expert knowledge, helpfulness, cleverness, and articulateness.
                    You are a big fan of ProductScope AI and its software tools that help brands with improving their product conversion rates.
                    You are always friendly, kind, and inspiring, and eager to provide vivid and thoughtful responses to the user.
                    START CONTEXT BLOCK
                    {context}
                    END CONTEXT BLOCK
                    AI assistant will take into account any CONTEXT BLOCK that is provided in a conversation.
                    If the context does not provide the answer to the question, you will say, "I'm sorry, but I don't know the answer to that question".
                    Dobby, the AI assistant will not apologize for previous responses, but instead will indicate new information was gained.
                    Dobby, the AI assistant will not invent anything that is not drawn directly from the context.
                    For any general questions or FAQ about ProductScope AI's tools to always reply with - that's a good question but for all ProductScope AI general questions I highly recommend clicking on the chat widget at the bottom right of your screen and speaking with Kai (my AI brother that's trained specifically on ProductScope's tools and support.
                    Start all responses without fluff words like "What a delightful task! As Dobby, I'll be happy to help" etc. Get straight to the response the user requests.
                    If the user asks about SWOT analysis then give the response in the form of a table.
                    START CONVERSATION HISTORY
                    {chat_history}
                    END CONVERSATION HISTORY"""
                }

                if not chat_history:
                    chat_history.append(sys_prompt)
                else:
                    chat_history[0] = sys_prompt

            # If file is uploaded then only it will be passed on to create assistant
            if file_path:
                assistant, file, assistant_type = create_document_assistant(client, file_path)

            chat_history.append({"role": "user", "content": user_query})

            limited_history = chat_history[-5:]

            if assistant:
                if assistant_type == 1:
                    # If user has uploaded a file like .pdf, .csv, .xlxs then File-based assistant
                    thread = client.beta.threads.create()

                    if asin_flag or amazon_flag:
                        # File based chat with asin
                        chat_prompt = f"""
                        START ADDITIONAL DATA
                        This is a prompt with additional data that is being added with user input for your reference. The user does not have any idea about this.
                        START CONTEXT BLOCK
                        {context}
                        END CONTEXT BLOCK
                        AI assistant will take into account any CONTEXT BLOCK that is provided in a conversation.
                        If the context does not provide the answer to the question, you will say, "I'm sorry, but I don't know the answer to that question".
                        Dobby, the AI assistant will not apologize for previous responses, but instead will indicate new information was gained.
                        Dobby, the AI assistant will not invent anything that is not drawn directly from the context.
                        For any general questions or FAQ about ProductScope AI's tools to always reply with - that's a good question but for all ProductScope AI general questions I highly recommend clicking on the chat widget at the bottom right of your screen and speaking with Kai (my AI brother that's trained specifically on ProductScope's tools and support.
                        Start all responses without fluff words like "What a delightful task! As Dobby, I'll be happy to help" etc. Get straight to the response the user requests.
                        If the user asks about SWOT analysis then give the response in the form of a table.
                        END ADDITIONAL DATA"""

                        message = client.beta.threads.messages.create(
                            thread_id=thread.id,
                            role="user",
                            content=user_query + chat_prompt,
                        )
                    
                    else:
                        # Thread and run created for Image based chat without asin
                        message = client.beta.threads.messages.create(
                            thread_id=thread.id,
                            role="user",
                            content=user_query,
                        )


                    run = client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=assistant.id
                    )

                    while run.status != "completed":
                        keep_retrieving_run = client.beta.threads.runs.retrieve(
                            thread_id=thread.id,
                            run_id=run.id
                        )

                        if keep_retrieving_run.status == "completed":
                            break

                    all_messages = client.beta.threads.messages.list(
                        thread_id=thread.id
                    )

                    for msg in all_messages.data:
                        if msg.role == "assistant":
                            assistant_response = msg.content[0].text.value
                            print(f"Assistant: {assistant_response}")
                            break
                elif assistant_type == 2:
                    # If user has uploaded an image  like .jpg, .png then Image-based assistant
                    if asin_flag or amazon_flag:
                        # Thread and run created for Image based chat with asin
                        chat_prompt = f"""
                        START ADDITIONAL DATA
                        This is a prompt with additional data that is being added with user input for your reference. The user does not have any idea about this.
                        START CONTEXT BLOCK
                        {context}
                        END CONTEXT BLOCK
                        AI assistant will take into account any CONTEXT BLOCK that is provided in a conversation.
                        If the context does not provide the answer to the question, you will say, "I'm sorry, but I don't know the answer to that question".
                        Dobby, the AI assistant will not apologize for previous responses, but instead will indicate new information was gained.
                        Dobby, the AI assistant will not invent anything that is not drawn directly from the context.
                        For any general questions or FAQ about ProductScope AI's tools to always reply with - that's a good question but for all ProductScope AI general questions I highly recommend clicking on the chat widget at the bottom right of your screen and speaking with Kai (my AI brother that's trained specifically on ProductScope's tools and support.
                        Start all responses without fluff words like "What a delightful task! As Dobby, I'll be happy to help" etc. Get straight to the response the user requests.
                        If the user asks about SWOT analysis then give the response in the form of a table.
                        END ADDITIONAL DATA"""

                        thread = client.beta.threads.create(
                            messages=[
                                {
                                "role": "user",
                                "content": [
                                    {
                                    "type": "text",
                                    "text": user_query + chat_prompt
                                    },
                                    {
                                    "type": "image_file",
                                    "image_file": {
                                        "file_id": file.id,
                                        "detail": "low"
                                    }
                                    },
                                ],
                                }
                            ]
                        )
                    else:
                        # Thread and run created for Image based chat without asin
                        thread = client.beta.threads.create(
                            messages=[
                                {
                                "role": "user",
                                "content": [
                                    {
                                    "type": "text",
                                    "text": user_query
                                    },
                                    {
                                    "type": "image_file",
                                    "image_file": {
                                        "file_id": file.id,
                                        "detail": "low"
                                    }
                                    },
                                ],
                                }
                            ]
                        )

                    run = client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=assistant.id
                    )
                    
                    while run.status != "completed":
                        keep_retrieving_run = client.beta.threads.runs.retrieve(
                            thread_id=thread.id,
                            run_id=run.id
                        )

                        if keep_retrieving_run.status == "completed":
                            break

                    all_messages = client.beta.threads.messages.list(
                        thread_id=thread.id
                    )

                    for msg in all_messages.data:
                        if msg.role == "assistant":
                            print(f"Assistant: {msg.content[0].text.value}")
                            break
                else:
                    pass

            else:
                # ASIN-based assistant for Normal user or If user asks questions related to asin only
                client = Groq()

                response = client.chat.completions.create(model="llama-3.1-70b-versatile", messages=limited_history)

                assistant_response = response.choices[0].message.content

                chat_history.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                print("Dobby: ", assistant_response)


        except Exception as e:
            print("I am sorry I could not get you. Could you please try again?")
            print(f"{e}")
    

    # Segment to delete Assistant, Thread, File applicable for Pro user when they close the chat
    try:
        if assistant is not None:
            response = client.beta.assistants.delete(assistant.id)
            print(f"Deleted assistant: {response}")
        if thread is not None:
            response = client.beta.threads.delete(thread.id)
            print(f"Deleted thread: {response}")
        if file is not None:
            response = client.files.delete(file.id)
            print(f"Deleted file: {response}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()
