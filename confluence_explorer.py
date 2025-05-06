import requests
import openai
import re
from typing import Dict, Any

class ConfluenceExplorer:
    def __init__(self, base_url: str, username: str, api_token: str, openai_key: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, api_token)
        openai.api_key = openai_key

    def search_confluence(self, query: str) -> list:
        """Search Confluence for pages matching the query."""
        # For Confluence Cloud, we need to use the correct API endpoint
        url = f"{self.base_url}/wiki/rest/api/content/search"
        # Use a more flexible search pattern
        search_query = query.lower()
        cql = f'title ~ "{search_query}" OR text ~ "{search_query}"'
        params = {
            'cql': cql,
            'limit': 5  # Increased limit to 5 results
        }
        
        try:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            response = requests.get(url, params=params, auth=self.auth, headers=headers)
            response.raise_for_status()
            results = response.json().get('results', [])
            
            # Print search details for debugging
            print(f"\nSearch details:")
            print(f"Search query: {search_query}")
            print(f"CQL query: {cql}")
            print(f"Found {len(results)} results")
            
            return results
        except Exception as e:
            print(f"\nSearch error: {e}")
            print(f"Response status: {response.status_code if 'response' in locals() else 'N/A'}")
            print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
            return []

    def get_page_content(self, page_id: str) -> str:
        """Get the content of a specific page."""
        url = f"{self.base_url}/wiki/rest/api/content/{page_id}?expand=body.storage"
        
        try:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            response = requests.get(url, auth=self.auth, headers=headers)
            response.raise_for_status()
            content = response.json()['body']['storage']['value']
            # Remove HTML tags
            clean_content = re.sub('<[^>]+>', '', content)
            # Limit content length to prevent token overflow
            max_length = 10000  # Adjust this based on your needs
            if len(clean_content) > max_length:
                clean_content = clean_content[:max_length] + "... (content truncated)"
            return clean_content.strip()
        except Exception as e:
            print(f"Content fetch error: {e}")
            print(f"Response status: {response.status_code if 'response' in locals() else 'N/A'}")
            print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
            return ""

    def ask_ai(self, question: str, context: str) -> str:
        """Ask AI about the content."""
        try:
            # Split context into chunks if it's too long
            max_context_length = 8000  # Adjust based on model limits
            if len(context) > max_context_length:
                context = context[:max_context_length] + "... (context truncated)"
            
            # Enhanced system prompt with detailed instructions
            system_prompt = """
You are a highly skilled technical analyst and QA expert. Your task is to analyze Confluence content and provide accurate, concise answers to questions.

Instructions:
1. Carefully read and understand the provided context
2. Identify key technical concepts and their relationships
3. Provide clear, step-by-step explanations when requested
4. Include relevant technical details and best practices
5. If the question asks for a process or procedure:
   - Break it down into clear, numbered steps
   - Include any prerequisites or requirements
   - Highlight important considerations or potential issues
6. If the context is truncated:
   - Focus on the available information
   - Clearly state what can be determined from the provided content
   - Note any limitations in the analysis
7. Format your response in a clear, structured way:
   - Use bullet points for lists
   - Use numbered steps for processes
   - Include relevant technical terms with explanations
8. Be specific and detailed in your analysis
9. If you're unsure about any aspect, clearly state what information would be needed to provide a more complete answer
"""

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
                ],
                temperature=0.3,
                max_tokens=1000,  # Increased token limit for more detailed responses
                top_p=0.9,  # Controls diversity of responses
                frequency_penalty=0.2,  # Encourages variety
                presence_penalty=0.2,  # Encourages new ideas
            )
            
            # Process the response to make it more structured
            raw_response = response.choices[0].message.content
            
            # Add a summary header if not present
            if not raw_response.startswith("Summary:"):
                response_text = f"Summary:\n{raw_response}"
            else:
                response_text = raw_response
            
            return response_text
            
        except Exception as e:
            error_msg = f"AI error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nError details: {e.response.json()}"
            return error_msg

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    # Get credentials from environment variables
    CONFLUENCE_URL = os.getenv('CONFLUENCE_URL')
    USERNAME = os.getenv('CONFLUENCE_USERNAME')
    API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN')
    OPENAI_KEY = os.getenv('OPENAI_API_KEY')
    
    if not all([CONFLUENCE_URL, USERNAME, API_TOKEN, OPENAI_KEY]):
        print("Error: Missing required environment variables")
        print("Please set: CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN, OPENAI_API_KEY")
        return

    explorer = ConfluenceExplorer(CONFLUENCE_URL, USERNAME, API_TOKEN, OPENAI_KEY)

    # Interactive demo
    search_term = input("Enter search term: ")
    pages = explorer.search_confluence(search_term)
    
    if not pages:
        print("No pages found!")
        return

    print(f"\nFound {len(pages)} relevant pages:")
    for i, page in enumerate(pages, 1):
        print(f"{i}. {page.get('title', 'Untitled')}")

    # Get content from all found pages first
    all_content = []
    page_titles = []
    for page in pages:
        content = explorer.get_page_content(page['id'])
        all_content.append(content)
        page_titles.append(page.get('title', 'Untitled'))

    # Generate QA-focused suggested questions based on actual page content
    suggested_questions = []
    
    # Analyze page titles to generate relevant QA questions
    for title in page_titles:
        # Extract key topics from the title
        topics = []
        if "proctor" in title.lower():
            topics.extend([
                "Proctor Test",
                "Test Bucket",
                "A/B Testing"
            ])
        if "gtm" in title.lower() or "tag manager" in title.lower():
            topics.extend([
                "GTM Implementation",
                "Data Layer",
                "Event Tracking"
            ])
        if "qa" in title.lower() or "testing" in title.lower():
            topics.extend([
                "QA Strategy",
                "Test Cases",
                "Automation"
            ])
        
        # Generate questions based on detected topics
        for topic in topics:
            suggested_questions.extend([
                f"Create a QA testing strategy for {topic}",
                f"What are the key validation points for {topic} testing?",
                f"How to create effective test cases for {topic}?",
                f"Best practices for testing {topic}",
                f"Common QA challenges in {topic} implementation",
                f"How to track and report {topic} test results",
                f"What metrics should QA track for {topic} testing?",
                f"Best practices for {topic} test documentation",
                f"How to create a {topic} regression test suite",
                f"Common issues and troubleshooting for {topic} testing"
            ])

    # Remove duplicates and limit to 10 most relevant questions
    suggested_questions = list(dict.fromkeys(suggested_questions))[:10]

    # Add general QA questions if we have fewer than 5 questions
    if len(suggested_questions) < 5:
        general_qa_questions = [
            "Create a comprehensive QA testing strategy",
            "What are the key testing phases and their objectives?",
            "How to create effective test cases and test plans",
            "Best practices for test automation",
            "How to implement continuous testing",
            "Common QA challenges and solutions",
            "How to measure QA effectiveness",
            "Best practices for test documentation",
            "What metrics should QA track?",
            "How to improve QA processes"
        ]
        suggested_questions.extend(general_qa_questions[:5 - len(suggested_questions)])

    # Print the found pages and their titles
    print("\nFound relevant pages:")
    for i, title in enumerate(page_titles, 1):
        print(f"{i}. {title}")

    print("\nSuggested QA questions based on found pages:")
    for i, question in enumerate(suggested_questions, 1):
        print(f"{i}. {question}")

    print("\nSuggested questions:")
    for i, question in enumerate(suggested_questions, 1):
        print(f"{i}. {question}")

    print("\nChoose a question number or enter your own question:")
    choice = input("Enter question number or type your question: ")

    # Get the question based on user choice
    if choice.isdigit():
        choice_num = int(choice)
        if 1 <= choice_num <= len(suggested_questions):
            question = suggested_questions[choice_num - 1]
        else:
            print("Invalid question number. Using default question.")
            question = "Please provide more details about this topic"
    else:
        question = choice

    # Get content from all found pages
    all_content = []
    for page in pages:
        content = explorer.get_page_content(page['id'])
        all_content.append(content)

    answer = explorer.ask_ai(question, "\n\n".join(all_content))
    print("\nAnswer:", answer)

if __name__ == "__main__":
    main()