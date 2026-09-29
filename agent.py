import requests
import re
import json


# LOAD MEMORY


try:
    with open("memory.json", "r") as f:
        memory = json.load(f)

        if not isinstance(memory, dict):
            memory = {}

except:
    memory = {}


# OLLAMA CHAT


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


# CALCULATOR TOOL


def calculator(a, b, op):

    if op == "+":
        return a + b

    elif op == "-":
        return a - b

    elif op == "*":
        return a * b

    elif op == "/":

        if b == 0:
            return "Cannot divide by zero"

        return a / b

    return "Unknown operation"


# CITY EXTRACTION


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


# WEATHER TOOL


def weather(city):

    try:

        url = f"https://wttr.in/{city}?format=j1"

        response = requests.get(url)

        if response.status_code != 200:
            return "Weather service unavailable"

        data = response.json()

        temp = data["current_condition"][0]["temp_C"]

        return f"{city}: {temp}°C"

    except Exception as e:

        return f"Weather Error: {e}"


# TOOL SELECTION


def choose_tool(user_input):

    user_input = user_input.lower()

    if any(op in user_input for op in ["+", "-", "*", "/"]):
        return "calculator"

    elif "weather" in user_input:
        return "weather"

    else:
        return "none"


# START


print("Ghost Agent Started!")
print("Type 'exit' to quit.\n")

# MAIN LOOP


while True:

    user_input = input("you: ")

    if user_input.lower() == "exit":
        print("Ghost: Goodbye!")
        break

    # NAME MEMORY SAVE


    if "my name is" in user_input.lower():

        name = user_input.lower().replace(
            "my name is", ""
        ).strip()

        memory["name"] = name

        with open("memory.json", "w") as f:
            json.dump(memory, f, indent=4)

        print(f"Ghost: Nice to meet you, {name}!")

        continue


    # NAME MEMORY RECALL


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

  
    # CITY MEMORY SAVE
   

    if "i live in" in user_input.lower():

        city = user_input.lower().replace(
            "i live in", ""
        ).strip()

        memory["city"] = city

        with open("memory.json", "w") as f:
            json.dump(memory, f, indent=4)

        print(
            f"Ghost: I'll remember that you live in {city}"
        )

        continue

    
    # CITY MEMORY RECALL
   

    if "where do i live" in user_input.lower():

        if "city" in memory:

            print(
                f"Ghost: You live in {memory['city']}"
            )

        else:

            print(
                "Ghost: I don't know where you live yet."
            )

        continue

    
    # TOOL SELECTION
   

    tool = choose_tool(user_input)

    print("Selected Tool:", tool)

   
    # CALCULATOR
   

    if tool == "calculator":

        numbers = re.findall(r"\d+", user_input)

        if len(numbers) >= 2:

            a = int(numbers[0])
            b = int(numbers[1])

            if "+" in user_input:
                op = "+"

            elif "-" in user_input:
                op = "-"

            elif "*" in user_input:
                op = "*"

            elif "/" in user_input:
                op = "/"

            else:
                op = None

            result = calculator(a, b, op)

            print("Ghost:", result)

        else:

            print("Ghost: Could not find numbers")

    
    # WEATHER
    

    elif tool == "weather":

        city = extract_city(user_input)

        print("Extracted City:", city)

        result = weather(city)

        print("Ghost:", result)

    # NORMAL CHAT
 

    else:

        answer = ask_ollama(user_input)

        print("Ghost:", answer)
