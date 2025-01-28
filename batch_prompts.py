from openai import OpenAI
import json
import pandas as pd
import argparse
import os
import sys
from pypdf import PdfReader
from prompts import CompleteAssessment

client = OpenAI()

parser = argparse.ArgumentParser(description="Process PDF files and generate a AI summary.")
parser.add_argument("folder_path", type=str, help="The folder path containing the PDF files.")
parser.add_argument("json_file_path", type=str, help="The file path to the JSON prompts.")

# Parse arguments
args = parser.parse_args()
folder_path = args.folder_path
json_file_path = args.json_file_path

# Check if folder_path is a valid directory
if not os.path.isdir(folder_path):
    print(f"Error: {folder_path} is not a valid directory.")
    sys.exit(1)
    
# Check if json_file_path is a valid file
if not os.path.isfile(json_file_path):
    print(f"Error: {json_file_path} is not a valid file.")
    sys.exit(1)
    
# Check if OPENAI_API_KEY is set in environment variables
if 'OPENAI_API_KEY' not in os.environ:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    sys.exit(1)
else:
    print("OPENAI_API_KEY environment variable is set.")


def create_batch_tasks():
    # read data from the JSON file
    prompt = ""
    query_data = {}
    with open(json_file_path, 'r') as json_file:
        query_data = json.load(json_file)
        prompt = json.dumps(query_data)
        
    # Creating an array of json tasks

    tasks = []

    # loop over all files in the specified folder
    for index, filename in enumerate(os.listdir(folder_path)):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            
            try:
                # create a pdf reader object
                print(f"Processing file: {filename}")
                reader = PdfReader(file_path)
            except Exception as e:
                print(f"Error reading file: {e}")
                continue
            
            # get the number of pages in the pdf file
            num_pages = len(reader.pages)
            # print(f"Number of pages in {filename}: {num_pages}")
            
            # combine text from all pages
            combined_text = ""
            # loop over all pages and extract text
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                # print(f"Text from {filename}, page {page_num + 1}:\n{text}\n")
                combined_text += text
            
            # count the number of words in the combined text
            word_count = len(combined_text.split())
            # print(f"Text extracted: {combined_text}")
            
            # execute the AI promt
            if word_count == 0:
                print("Error: file contains no text.")
            else:
                task = {
                    "custom_id": f"task-{index}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": "gpt-4o-mini",
                        "temperature": 0.1,
                        "response_format": { 
                            'type': 'json_schema',
                                'json_schema': 
                                    {
                                        "name":"whocares", 
                                        "schema": CompleteAssessment.model_json_schema()
                                    }
                                },
                        },
                        "messages": [
                            {
                                "role": "system",
                                "content": prompt
                            },
                            {
                                "role": "user",
                                "content": combined_text
                            }
                        ],
                    }   
                tasks.append(task)
        
    file_name = "data/batch_tasks_movies.jsonl"

    with open(file_name, 'w') as file:
        for obj in tasks:
            file.write(json.dumps(obj) + '\n')
            
            
    batch_file = client.files.create(
    file=open(file_name, "rb"),
    purpose="batch"
    )

    batch_job = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"
    )
    print("Batch id:" + batch_job.id)

    
def load_results(batchId):   
    batch_job = client.batches.retrieve(batchId)
    print(batch_job)
    
    result_file_id = batch_job.output_file_id
    result = client.files.content(result_file_id).content

    result_file_name = "batch_job_results_movies.jsonl"

    with open(result_file_name, 'wb') as file:
        file.write(result)
            
    # Loading data from saved file
    results = []
    with open(result_file_name, 'r') as file:
        for line in file:
            # Parsing the JSON string into a dict and appending to the list of results
            json_object = json.loads(line.strip())
            results.append(json_object)
            
    # Reading only the first results
    for res in results[:5]:
        task_id = res['custom_id']
        # Getting index from task id
        index = task_id.split('-')[-1]
        result = res['response']['body']['choices'][0]['message']['content']
        movie = df.iloc[int(index)]
        description = movie['Overview']
        title = movie['Series_Title']
        print(f"TITLE: {title}\nOVERVIEW: {description}\n\nRESULT: {result}")
        print("\n\n----------------------------\n\n")