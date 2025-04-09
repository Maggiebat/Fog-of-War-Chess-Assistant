import requests
import re

class OutputProcessor:
    def __init__(self):
        # Hugging Face API key:
        self.api_key = "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"
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    # Sends user input to Hugging Face API & retrieves output:
    def get_mistral_output(self, move_suggestion):
        prompt = (
            f"You are a friendly but professional chess assistant. You are aiding one advantaged player. Given the limited information available in a Fog of War setting, respond to the following move suggestion with a one-paragraph explanation in a mildly friendly, casual tone. "
            f"Use chess piece names like Queen, Bishop, or Rook. Do not repeat the instructions.\n\n"
            f"Move Suggestion: {move_suggestion}"
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
        # Split into lines and remove lines that match known instruction patterns
        lines = response_text.strip().splitlines()

        # Filter out lines that clearly match the prompt pattern
        filtered_lines = [
            line for line in lines
            if not (
                line.lower().startswith("convey the following") or
                "fog of war" in line.lower() or
                "use words" in line.lower() or
                "move suggestion" in line.lower() or
                line.strip() == ""
            )
        ]

        # Rejoin what's left
        cleaned_response = " ".join(filtered_lines).strip()

        # Remove "Response:" or "response:" if it starts the cleaned output
        if cleaned_response.lower().startswith("response:"):
            cleaned_response = cleaned_response[len("response:"):].strip()

        # Capitalize if the model started mid-sentence
        if cleaned_response and cleaned_response[0].islower():
            cleaned_response = cleaned_response[0].upper() + cleaned_response[1:]

        return cleaned_response



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
