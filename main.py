import os
import csv
import json
from pypdf import PdfReader
from prompts import execute_prompt, validate_text_prompt
from datetime import datetime

# read data from the JSON file
json_file_path = "query.json"
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
    
# accept the folder path as an input from the console
folder_path = input("Please enter the folder path containing the PDF files: ")

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
        
        # execute the AI promt
        # prompt = f"You are a school teacher evaluating a student's essay. Evaluate the follow essay written by a student on the topic '{topic}'. Provide your answer in bullet form. For each of the below assessment criteria, provide a grade between A to F \nNo explanation needed."
        
        response = execute_prompt(filename, prompt, combined_text)
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