import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv
import random
from colorama import Fore, Style

#i used a .Env file to store the api key
#bonuses i implemented:
#1. colored text
#2. auto format using black
# List of random programs
PROGRAMS_LIST = [
    '''Given two strings str1 and str2, prints all interleavings of the given two strings. You may assume that all characters in both strings are different. Input: str1 = "AB", str2 = "CD" Output: ABCD ACBD ACDB CABD CADB CDAB Input: str1 = "AB", str2 = "C" Output: ABC ACB CAB''',
    "a program that checks if a number is a palindrome",
    "A program that finds the kth smallest element in a given binary search tree.",
    # add 2 more
    "Create a tool for complex data visualizations that can handle large datasets and offer various types of charts and graphs, with interactive features like zooming, panning, and tooltip displays."
    "Write a program that takes a partially filled Sudoku grid and outputs a completed grid if a solution exists. The program should use backtracking to find the solution."
    #Hard code that fails the program usually:
    #"Develop a connect-4 game (like chess or tic-tac-toe) where users can play against AI opponents. The AI should use algorithms or machine learning to improve its gameplay over time."

]


def generate_code(client, prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo"
    )
    return chat_completion.choices[0].message.content

def main():
    load_dotenv()
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    user_request = input(Fore.CYAN + "Tell me, which program would you like me to code for you? If you don't have an idea, just press enter and I will choose a random program to code.\n")

    if not user_request:
        user_request = random.choice(PROGRAMS_LIST)

    attempts = 0
    success = False
    #add a request for unit tests
    while attempts < 5 and not success:
        user_request += " Also please include unit tests that check the logic of the program using 5 different inputs and expected outputs and prints it to the screen. and please write the whole python code in one block of code in you answer."

        response_text = generate_code(client, user_request)
        start = response_text.find("```python") + len("```python\n")
        end = response_text.find("```", start)
        python_code = response_text[start:end].strip()

        file_path = "generatedcode.py"
        with open(file_path, "w") as file:
            file.write(python_code)

        try:
            subprocess.run(["python3", file_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(Fore.GREEN + "Code creation completed successfully !")
            #black format
            subprocess.run(['black', file_path], check=True)
            subprocess.call(["open", file_path])
            # use this call to open the file on Windows
            #subprocess.call(f"start {file_path}", shell=True)
            success = True
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error running generated code! Error: {e.stderr}")
            user_request = f"The code is'nt working! I want you to rewrite the WHOLE code again from the beginning! and fix the errors. these are the errors and the code: {e}\n\n{python_code}"
            attempts += 1
            #print(e.stderr)
            #print(user_request)
        print(Style.RESET_ALL)
    if not success:
        print(Fore.RED + "Code generation FAILED")
    

main()

