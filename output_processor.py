import requests
import re

class OutputProcessor:
    def __init__(self):
        # Hugging Face API key:
        self.api_key = "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"
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    # Sends user input to Hugging Face API & retrieves output:
    def get_mistral_output(self, move_suggestion):
        prompt = (
            f"Convey the following chess move suggestion in a mildly friendly (but stil professional), casual tone: {move_suggestion} "
            "Just provide the move suggestion and thorough explanation, given the information that you have in the limited Fog of War environment."
            "Avoid unnecessary phrases such as 'hey there', 'hope this helps', and 'have fun, and 'good luck.'"
            "Do not call the user 'friend.'"
        )

        # API request to Hugging Face:
        data = {"inputs": prompt}
        response = requests.post(self.api_url, headers=self.headers, json=data)

        if response.status_code == 200:
            result = response.json()
            raw_output = result[0]["generated_text"].strip() if result else "No response generated."
            return self.clean_response(raw_output)
        else:
            return f"Error: {response.status_code} - {response.text}"

    # Removes unnecessary instructions from the LLM output:
    def clean_response(self, response_text):
        """
        Removes everything before 'Suggested Move:' to keep only the move suggestion and explanation.
        """
        keyword = "Example:"
        if keyword in response_text:
            return response_text.split(keyword, 1)[-1].strip()  # Keep only the part after "'friend.'"
        return response_text  # If keyword not found, return original response

    # Takes engine move suggestion output & returns Assistant message to user:
    def main(self, move_suggestion):
        output = self.get_mistral_output(move_suggestion)
        return output


if __name__ == "__main__":

    # Example engine output:
    ex_engine_move_suggestion = "Suggested Move: Move Q from D1 to D6."

    # Instantiate class:
    processor = OutputProcessor()

    # Process move suggestion:
    result = processor.main(ex_engine_move_suggestion)

    print("\n", "The move suggestion from the engine was: ", '"' + ex_engine_move_suggestion + '"')
    print("Output Processor output: ", result, "\n")
