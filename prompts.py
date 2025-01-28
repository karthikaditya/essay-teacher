import openai
import os
from datetime import datetime
import time
from pydantic import BaseModel, ValidationError
import logging

class AsssessmentGrade(BaseModel):
    criteria: str
    explanation: str
    grade: str
    
class CompleteAssessment(BaseModel):
    grades: list[AsssessmentGrade]

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')
# print(openai.api_key)

# Generate a unique log file name with date and time
log_filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure logging
logging.basicConfig(filename=log_filename, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def api_ping():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "ping"},
            ],
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.2,
        )
        return "API is up and running." + response.choices[0].message['content']
    except openai.error.RateLimitError as e:
        return f"Rate limit exceeded. Please try again later."
    except openai.error.OpenAIError as e:
        return f"An error occurred with OpenAI: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

def validate_text_prompt(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "What's your opinion on the following text?"},
                {"role": "user", "content": text},
            ],
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.2,
        )
        return response.choices[0].message['content']
    except openai.error.RateLimitError as e:
        return f"Rate limit exceeded. Please try again later."
    except openai.error.OpenAIError as e:
        return f"An error occurred with OpenAI: {e}"
    except Exception as e:
        return f"An error occurred: {e}"
    
def execute_prompt(filename, prompt, text):
    max_retries = 5
    retry_delay = 10  # seconds

    for attempt in range(max_retries):
        try:
            logging.info(f"Processing file: {filename}")
            
            response = openai.ChatCompletion.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                max_completion_tokens=4096,
                n=1,
                stop=None,
                temperature=0.2,
                # response_format=CompleteAssessment,
                response_format={
                    'type': 'json_schema',
                    'json_schema': 
                        {
                            "name":"whocares", 
                            "schema": CompleteAssessment.model_json_schema()
                        }
                    },
            )
            #response_text = response.choices[0].message['content'].strip()
            
            response_obj = {}
            try:
                # Parse and validate the response content
                response_obj = CompleteAssessment.model_validate(response.choices[0].message.content)
                print("Response parsed and validated successfully.")
            except ValidationError as e:
                # Handle validation errors
                print("Failed to parse response content.")
                # response_obj = e.json()
                
            # Log the prompt and response
            # logging.info(f"Response: {response}")
            
            return response_obj
        except openai.error.RateLimitError as e:
            logging.error(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
            print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        except openai.error.OpenAIError as e:
            logging.error(f"An error occurred: {e}")
            print(f"An error occurred with OpenAI: {e}")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return "Error: Unable to execute text due to rate limit."

# Example usage
# text = "Write a short inspiring and funny poem about Geeks for Geeks"
# response = api_ping()
# print("Response:", response)