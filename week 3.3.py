from collections import deque

faq_db = {
    "library timings": "Library is open from 9 AM to 9 PM.",
    "food court timings": "Food court is open from 8 AM to 9 PM.",
    "sports complex timings": "Sports complex is open from 6 AM to 8 AM and 4:30 PM to 7 PM."
}

campus_map = {
    "Main Gate": ["Admin Block"],
    "Admin Block": ["Library (inside Admin)", "Engineering Block"],
    "Library (inside Admin)": [],
    "Engineering Block": ["Food Court"],
    "Food Court": ["Football Court", "Hostel Block 1"],
    "Football Court": [],
    "Hostel Block 1": ["Sports Road"],
    "Sports Road": ["Cricket Ground", "Basketball Court", "Volleyball Court"],
    "Cricket Ground": [],
    "Basketball Court": [],
    "Volleyball Court": []
}

def shortest_path(graph, start, goal):
    visited = set()
    queue = deque([[start]])
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            for neighbor in graph.get(node, []):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
            visited.add(node)
    return None

def answer_query(user_input):
    user_input = user_input.lower()

    # Greeting
    if user_input in ["hi", "hello", "hey"]:
        return "Hello! How can I help you today?"

    # FAQ
    for key in faq_db:
        if key in user_input:
            return faq_db[key]

    # Detect locations in input
    places_mentioned = [place for place in campus_map if place.lower() in user_input]

    if len(places_mentioned) >= 2:
        path = shortest_path(campus_map, places_mentioned[0], places_mentioned[1])
        if path:
            return f"Shortest path: {' -> '.join(path)}"
        else:
            return "No path found between these locations."

    return "Sorry, I don't understand that. Try asking about timings or specify two campus locations for directions."

if __name__ == "__main__":
    print("Campus Chatbot Ready! (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break
        response = answer_query(user_input)
        print("Chatbot:", response)
