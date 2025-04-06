import json
import requests

class InputProcessor:
    def __init__(self):
        # Hugging Face API key:
        self.api_key = "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"
        self.mistral_api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    # Gets structured response from Mistral:
    def get_mistral_output(self, user_input):
        prompt = (
            "You are a helpful assistant. Respond **only** in JSON format with these fields:\n"
            "1. 'severity': A score (1-5) based on urgency according to the user.\n"
            "2. 'piece': The opponent's chess piece involved.\n"
            "3. 'action': The exact desired action (counter, punish, take, analyze, etc).\n"
            "4. 'preference': Whether the user is saying directly that the opponent overuses the piece (true/false).\n"
            "5. 'force forks': Whether the user is saying directly that the opponent tries to force forks (true/false).\n"
            f"User input: {user_input}\n\n"
            "Respond **ONLY** with a valid JSON object, with no extra text, explanations, or greetings."
        )

        data = {"inputs": prompt}
        response = requests.post(self.mistral_api_url, headers=self.headers, json=data)

        if response.status_code == 200:
            result = response.json()
            raw_output = result[0]["generated_text"].strip() if result else None

            if not raw_output:
                print("Warning: Empty response from Mistral")
                return None

            # print("Raw Mistral Output:", raw_output)  # for debugging
            return self.extract_json(raw_output)
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None

    # Extracts only the JSON portion from Mistral's response:
    def extract_json(self, response_text):
        try:
            # Remove markdown-style code blocks if present:
            response_text = response_text.replace("```json", "").replace("```", "").strip()

            # Split by newline to find first JSON block only:
            json_blocks = response_text.split("\n\n")
            for block in json_blocks:
                block = block.strip()
                if block.startswith("{") and block.endswith("}"):
                    return block  # return the first valid JSON block

            print("Warning: No valid JSON found in the response.")
            return None
        except Exception as e:
            print(f"JSON Extraction Error: {e}")
            return None

    # Parses JSON:
    def parse_structured_data(self, json_string):
        try:
            if json_string:
                data_dict = json.loads(json_string)

                def safe_int(value):
                    try:
                        return min(5, max(1, int(value)))  # clamp to 1–5
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid severity value: {value} — defaulting to 3")
                        return 3  # middle-ground fallback

                formatted_dict = {
                    "severity": safe_int(data_dict.get("severity", 3)),
                    "piece": str(data_dict.get("piece", "")).lower(),
                    "action": str(data_dict.get("action", "")).lower(),
                    "preference": bool(data_dict.get("preference", False)),
                    "force forks": bool(data_dict.get("force forks", False)),
                }
                return formatted_dict
            else:
                print("Warning: No valid JSON string provided for parsing.")
                return None
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw JSON String: {json_string}")
            return None


    # Main function to process user input:
    def main(self, user_input):
        output_str = self.get_mistral_output(user_input)

        if output_str:
            return self.parse_structured_data(output_str)
        else:
            print("No valid output received from Mistral.")
            return None


if __name__ == "__main__":
    processor = InputProcessor()
    
    # Test one example:
    user_input = "To win I must punish my opponent for over-utilizing the queen."
    result = processor.main(user_input)
    print('\n', "The user input was: ", '"' + user_input + '"')
    print("Input Processor Output:", result, '\n')

'''
    # Test all client-provided prompts (DO NOT DO THIS UNLESS STRICTLY NECESSARY):
    with open("test_user_inputs.json", "r", encoding="utf-8") as f:
        test_data = json.load(f)

    output_results = []  # to store all results

    for i, phrase in enumerate(test_data["inputs"], 1):
        print(f"\nTest Case #{i}")
        print(f"User input: {phrase}")
        result = processor.main(phrase)
        print(f"JSON output: {result}")

        output_results.append({
            "test_case": i,
            "user_input": phrase,
            "output": result
        })

    # Write results to a .txt file:
    output_path = "input_processor_results.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in output_results:
            f.write(f"Test Case #{entry['test_case']}\n")
            f.write(f"User input: {entry['user_input']}\n")
            f.write(f"JSON output: {entry['output']}\n\n")

    print(f"\nAll results saved to {output_path}")
'''
