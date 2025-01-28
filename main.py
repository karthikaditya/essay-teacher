import os
import csv
import json
import argparse
import sys
from pypdf import PdfReader
from prompts import execute_prompt, validate_text_prompt
from datetime import datetime

# accept the folder path as an input from the console
# folder_path = input("Please enter the folder path containing the PDF files: ")

# json_file_path = input("Please enter the file path to the json prompts:")

# Set up argument parser
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
    
# read data from the JSON file
prompt = ""
query_data = {}
with open(json_file_path, 'r') as json_file:
    query_data = json.load(json_file)
    prompt = json.dumps(query_data)
    
    # category = query_data.get("category", "")
    # topic = query_data.get("essayTopic", "")
    # assessments = query_data.get("assessments", [])
    
    # completed_assessments = ""
    # for index, assessment in enumerate(assessments):
    #     criteria = assessment.get("criteria", "")
    #     min_points = assessment.get("min_points", 0)
    #     max_points = assessment.get("max_points", 100)
    #     completed_assessments += f"CRITERIA {index}: {criteria}"
        # and assign a number score between minimum of {min_points} and maximum of {max_points})\n"
    
    # prompt = f"Topic: {topic}\nAssessments: {completed_assessments}\n"

# generate a unique CSV file name with date and time
output_csv = f"AIEssayReview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# list to store file names, word counts, and page counts
essay_response = []
    
# loop over all files in the specified folder
for filename in os.listdir(folder_path):
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
        # print(f"Word count for {filename}: {word_count}")
        # print(f"Text extracted: {combined_text}")
        
        # execute the AI promt
        if word_count == 0:
            print("Error: file contains no text.")
            response = "No text found in the PDF file."
        else:
            response = execute_prompt(filename, prompt, combined_text)
            
            # for res in response.grades:
            #     print(f"Grade: {res.criteria} - {res.grade}")
                
            # summary = validate_text_prompt(combined_text)
            # print(f"Summary of {filename}:\n{response}\n") 
            print("AI response obtained.")
            
        # add the file name, word count, and page count to the list
        essay_response.append([filename, word_count, num_pages, response])

# write the collected data to the CSV file
with open(output_csv, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    # write the header row
    csv_writer.writerow(["File Name", "Word Count", "Page Count", "AI Feedback"])
    # write the file names, word counts, and page counts
    csv_writer.writerows(essay_response)