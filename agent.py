import requests
import re
import json

try:
    with open("memory.json","r") as f:
        memory = json.load(f)

        if not isinstance(memory, dict):
            memory = {}
except:
    memory = {}


    

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

        if op == "+":
            return a + b

        elif op == "-":
            return a - b

        elif op == "*":
            return a * b

        elif op == "/":
            return a / b
        else:
            return "Unknown operation"



        

def extract_city(user_input):

    words = user_input.lower().split()

    if "in" in words:
        idx = words.index("in")

        if idx + 1 < len(words):
            return words[idx + 1].capitalize()

    if "of" in words:
        idx = words.index("of")

        if idx + 1 < len(words):
            return words[idx + 1].capitalize()

    return "Nagpur"

def weather(city):

    try:
        url = f"https://wttr.in/{city}?format=j1"

        response = requests.get(url)

        data = response.json()

        temp = data["current_condition"][0]["temp_C"]

        return f"{city}: {temp}°C"

    except Exception as e:
        return f"Weather Error: {e}"

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

    
    # MEMORY SAVE
    

    if "my name is" in user_input.lower():

        name = user_input.lower().replace(
            "my name is", ""
        ).strip()

        print(type(memory))
        print(memory)

        memory["name"] = name

        with open("memory.json","w") as f:
            json.dump(memory, f, indent=4)
        print("Memory Saved:", memory)

        print(f"Ghost: Nice to meet you, {name}!")

        continue

    
    # MEMORY RECALL
    

    if "what is my name" in user_input.lower():

        if "name" in memory:
            print(
                f"Ghost: Your name is {memory['name']}"
            )
        else:
            print(
                "Ghost: I don't know your name yet."
            )

        continue


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

        city = extract_city(user_input)

        print("Extracted City:", city)

        result =weather(city)

        print("Ghost:", result)

    else:


# Normal chat

        answer = ask_ollama(user_input)

        print('Ghost:', answer )
