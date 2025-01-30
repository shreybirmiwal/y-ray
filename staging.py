import json
from ollama import Client

def add_new_contact(input):
    client = Client()
    
    try:
        response = client.chat(
            model='deepseek-r1:1.5b',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant extracting information from a text. You need to extract the users contact info, ignoring info that does not fit into the json output items. Valid JSOn output items: {name, contact, birthday, job, facts, friends}. Always respond in valid JSON format. Example: {"name": "John Doe", "contact": "123-456-7890, john@gmail.com", "birthday": "", "job": "", "facts": "likes apples", "friends": ""}'
                },
                {
                    'role': 'user',
                    'content': input
                }
            ],
            options={
                'temperature': 0.0,
            }
        )
        
        print("Raw response:", response)
        
        # Check if 'message' and 'content' keys exist in the response
        if 'message' in response and 'content' in response['message']:
            content = response['message']['content']
            print("Response content:", content)
            
            content = content[content.indexOf('</think>'):]

            content = content.strip()
            content.replace('\n', '')

            print("NEW CONTENT ###")
            print(content)
            print("#####")
            
            # Try to parse the content as JSON
            try:
                json_response = json.loads(content)
                print("Parsed JSON:", json.dumps(json_response, indent=2))
                return json_response
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print("The content is not valid JSON. Returning the raw content instead.")
                return content
        else:
            print("Unexpected response format")
            return response
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Test the function
result = add_new_contact('lebron james, 5129427, 7299, apple works at appple?')
print("Result:", result)
