import requests
import re

def ask_ollama(prompt):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
            "temperature": 0
        }
    )

    data = response.json()

    return data["response"]




def calculator(a, b):
    return a + b

def weather(city):
    return f"{city}: 31C"

def choose_tool(user_input):

# def choose_tool(user_input):

    user_input = user_input.lower()

    if any(op in user_input for op in ["+", "-", "*", "/"]):
        return "calculator"

    elif "weather" in user_input:
        return "weather"

    else:
        return "none"
        prompt = f"""
        You are an AI agent.

        Available tools:
        1. calculator
        2. weather

        Rules:
        - Use calculator for math.
        - Use weather for weather questions.
        - Use none for normal chat.

        User: {user_input}

        Reply with ONLY one word:
        calculator
        weather
        none
        """

    return ask_ollama(prompt).strip().lower()

print("Ghost Agent Started!")
print("Type 'exit' to quit.\n")

while True:

    user_input = input("you:")

    if user_input.lower() == "exit":
        print("Ghost: Goodbye!")
        break
    tool = choose_tool(user_input)

    print("Raw Tool Response:", repr(tool))

    print("Selected Tool:", tool)

# Calculator Tool
    if tool == "calculator":

        numbers = re.findall(r"\d+", user_input)

        if len(numbers) >= 2:

            a = int(numbers[0])
            b = int(numbers[1])

            result = calculator(a, b)

            print("Ghost:", result)

        else:
            print("Ghost: Could not find numbers,")

# Weather Tool
    elif tool == "weather":

        city = "Nagpur"

        result =weather(city)

        print("Ghost:", result)

    else:


# Normal chat

        answer = ask_ollama(user_input)

        print('Ghost:', answer )
