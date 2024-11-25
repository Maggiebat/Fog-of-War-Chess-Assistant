import google.generativeai as genai
import json
import tkinter as tk
from tkinter import simpledialog

class InputProcessor:
    def __init__(self):
        # api key:
        genai.configure(api_key="AIzaSyDh37esnX-KiysJhqx9P1OeWGUw67xjNh8")
    
    def bias(self):
        root = tk.Tk()
        root.withdraw()
        input_value = simpledialog.askstring("Input", "Enter a value:")
        if input_value is not None:
            print("User input:", input_value)
        user_input = self.main(input_value)
        return user_input

    # sends user input to Gemini API & retrieves its output:
    def get_gemini_output(self, user_input):

        # get model:
        model = genai.GenerativeModel("gemini-1.5-flash-8b")

        # generate response:
        response = model.generate_content("You are part of a helpful Fog of War Chess Assistant. "
                "Structure the following user input into a JSON format with these fields: "
                "1. 'severity': a score based on the user's perceived urgency by using words like 'need' vs 'want', "
                                          "'must' or 'imperative', 'first priority' (1-5)."
                "2 'piece': the opponent's chess piece mentioned in the input. "
                "3. 'action': the desired action the user wants to take (counter, take, analyze, punish, remove, "
                                          "neutralize, etc). "
                "4. 'preference': whether the opponent has a preference for or over utilizes 'piece' (true or false). "
                "5. 'force forks': whether the opponent will try to force forks with 'piece' (true or false). "
                "Here is the input: " + user_input) # include user input in model prompt

        # return response as string:
        return response.text


    # turns gemini output into python dictionary:
    def parse_structured_data(self, input_string):

        # extract the JSON part of the string:
        start_index = input_string.find("```json") + len("```json")
        end_index = input_string.rfind("```")
        json_string = input_string[start_index:end_index].strip()

        # parse the JSON into a dictionary:
        data_dict = json.loads(json_string)

        # convert the values to the desired format:
        formatted_dict = {
            "severity": int(data_dict["severity"]),
            "piece": str(data_dict["piece"]),
            "action": str(data_dict["action"]),
            "preference": bool(data_dict["preference"]),
            "force forks": bool(data_dict["force forks"])
        }

        # return python dictionary:
        return formatted_dict


    # takes user input, returns dictionary structure of important information:
    def main(self, user_input):
        output_str = self.get_gemini_output(user_input)
        output_dict = self.parse_structured_data(output_str)

        return output_dict


if __name__ == "__main__":

    # example user input:
    # user_input = "To win I must punish my opponent for over utilizing queen"

    # instantiate class:
    processor = InputProcessor()

    user_input = processor.bias()

    # process input:
    result = processor.main(user_input)

    print(result)
