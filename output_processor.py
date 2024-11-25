import google.generativeai as genai
import json
import tkinter as tk
from tkinter import messagebox

class OutputProcessor:
    def __init__(self):
        # api key:
        genai.configure(api_key="AIzaSyDh37esnX-KiysJhqx9P1OeWGUw67xjNh8")

    # sends user input to Gemini API & retrieves its output:
    def get_gemini_output(self, move_suggestion):

        # get model:
        model = genai.GenerativeModel("gemini-1.5-flash-8b")

        # generate response:
        response = model.generate_content("You are part of a helpful Fog of War Chess Assistant. "
                "You are the part of the Assistant that conveys the move suggestion to the advantaged player that gets "
                                          "to use the Chess Assistant. Use your own discretion to deliver this message"
                                          "in a straightforward but mildly friendly tone. Keep it professional. Do not"
                                          "mention the engine as a separate entity. For the user, it is YOU making the"
                                          "suggestion, so make it sound as such."
                "Here is the move the engine came up with: " + move_suggestion) # include move suggestion from engine in model prompt

        # return response:
        return response.text


    # takes engine move suggestion output, returns Assistant chat message to relay to user:
    def main(self, move_suggestion):
        output = self.get_gemini_output(move_suggestion)
        messagebox.showinfo("Move Suggesstion", output)
        return output


if __name__ == "__main__":

    # example engine output:
    ex_engine_move_suggestion = "Suggested Move: Move Q from D1 to D6."

    # instantiate class:
    processor = OutputProcessor()

    # process move suggestion:
    result = processor.main(ex_engine_move_suggestion)

    print(result)
