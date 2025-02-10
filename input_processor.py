import google.generativeai as genai
import json
import re
import tkinter as tk
from tkinter import simpledialog

class InputProcessor:
    def __init__(self):
        # load API key from config file:
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                api_key = config.get("api_key")
                if not api_key:
                    raise ValueError("API key is missing from config.json")
        except FileNotFoundError:
            raise FileNotFoundError("config.json not found. Please create it with your API key.")

        # configure Gemini:
        genai.configure(api_key=api_key)

    def bias(self):
        root = tk.Tk()
        root.withdraw()
        input_value = simpledialog.askstring("Input", "Hello, what would you like me to do:")
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
                "Here is the input: " + user_input)

        # return response as string:
        return response.text


    # turns gemini output into python dictionary:
    def parse_structured_data(self, input_string):
        """
        Extracts only the JSON portion from the API response and parses it safely.
        """

        try:
            # Use regex to find the JSON object in the response
            match = re.search(r"\{.*\}", input_string, re.DOTALL)
            if match:
                json_string = match.group(0)  # Extract JSON part
                data_dict = json.loads(json_string)  # Parse JSON

                # Convert values to the desired format:
                formatted_dict = {
                    "severity": int(data_dict.get("severity", 0)),
                    "piece": str(data_dict.get("piece", "")),
                    "action": str(data_dict.get("action", "")),
                    "preference": bool(data_dict.get("preference", False)),
                    "force forks": bool(data_dict.get("force forks", False)),
                }

                return formatted_dict
            else:
                print("Error: Could not extract valid JSON from response.")
                return None

        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return None


    # takes user input, returns dictionary structure of important information:
    def main(self, user_input):
        output_str = self.get_gemini_output(user_input)
        output_dict = self.parse_structured_data(output_str)

        return output_dict


if __name__ == "__main__":

    # example user input:
    user_input = "To win I must punish my opponent for over utilizing queen"

    # instantiate class:
    processor = InputProcessor()

    # process input:
    result = processor.main(user_input)

    print(result)
