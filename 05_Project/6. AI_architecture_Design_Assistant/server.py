"""
AI Architecture Recommender - Flask Backend
=============================================
This server handles:
1. Receiving chat messages from the frontend
2. Sending them to OpenAI API (with tool descriptions)
3. Handling tool calls (executing the scoring functions)
4. Returning the final response to the frontend
"""

import json
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import n  # Your base recommender module

# ============================================================
# Flask app and OpenAI client setup
# ============================================================
app = Flask(__name__)
client = OpenAI(api_key="xxxxxx")  # ← Put your real API key here

# Store conversation history (in memory, resets when server restarts)
conversation_history = []

# ============================================================
# System prompt - tells LLM its role
# ============================================================
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are an AI architecture consultant. "
        "The user will describe their AI project requirements in natural language. "
        "Your job is to: "
        "1. Extract the 9 required parameters from the user's description. "
        "2. If any parameter is missing or unclear, ask the user for clarification. "
        "3. Once you have all parameters, call the analyze_project tool. "
        "4. Present the results in a clear, professional report using markdown formatting. "
        "Always respond in the same language the user uses."
    ),
}

# ============================================================
# Tool description - same as terminal Agent version
# ============================================================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_project",
            "description": "Analyze AI project requirements and recommend suitable architecture style, cloud service model, and deployment model.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the project",
                    },
                    "ai_workload": {
                        "type": "string",
                        "enum": ["nlp", "vision", "prediction", "expert_system"],
                        "description": "Type of AI workload",
                    },
                    "system_size": {
                        "type": "string",
                        "enum": ["small", "medium", "large"],
                        "description": "Size of the system",
                    },
                    "scalability": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Scalability requirement",
                    },
                    "real_time": {
                        "type": "string",
                        "enum": ["yes", "no"],
                        "description": "Whether real-time processing is required",
                    },
                    "budget": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Budget level",
                    },
                    "cloud_expertise": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Team cloud expertise level",
                    },
                    "data_sensitivity": {
                        "type": "string",
                        "enum": ["low", "high"],
                        "description": "Data sensitivity level",
                    },
                    "deployment_preference": {
                        "type": "string",
                        "enum": ["public", "private", "hybrid", "community"],
                        "description": "Preferred deployment model",
                    },
                },
                "required": [
                    "name",
                    "ai_workload",
                    "system_size",
                    "scalability",
                    "real_time",
                    "budget",
                    "cloud_expertise",
                    "data_sensitivity",
                    "deployment_preference",
                ],
            },
        },
    }
]


# ============================================================
# Tool execution function - same logic as terminal version
# ============================================================
def analyze_project(
    name,
    ai_workload,
    system_size,
    scalability,
    real_time,
    budget,
    cloud_expertise,
    data_sensitivity,
    deployment_preference,
):
    project = {
        "name": name,
        "ai_workload": ai_workload,
        "system_size": system_size,
        "scalability": scalability,
        "real_time": real_time,
        "budget": budget,
        "cloud_expertise": cloud_expertise,
        "data_sensitivity": data_sensitivity,
        "deployment_preference": deployment_preference,
    }

    architecture, scores = n.recommend_architecture(project)
    service_model = n.recommend_cloud_service_model(project, architecture)
    deployment_model = n.recommend_deployment_model(project, architecture)
    explanation = n.bulid_explanation(
        project, architecture, service_model, deployment_model
    )

    return {
        "project_name": name,
        "recommended_architecture": architecture,
        "architecture_scores": scores,
        "recommended_service_model": service_model,
        "recommended_deployment_model": deployment_model,
        "explanation": explanation,
    }


def handle_tool_call(tool_call):
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "analyze_project":
        result = analyze_project(**arguments)
        return json.dumps(result, indent=2)
    else:
        return json.dumps({"error": f"Unknown function: {function_name}"})


# ============================================================
# API Routes
# ============================================================


# Serve the frontend HTML page
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# Handle chat messages from frontend
@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Initialize conversation if empty
    if not conversation_history:
        conversation_history = [SYSTEM_MESSAGE]

    # Add user message to history
    conversation_history.append({"role": "user", "content": user_message})

    # First API call - send to LLM with tools
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2048,
        messages=conversation_history,
        tools=TOOLS,
    )

    assistant_message = response.choices[0].message

    # Check if LLM wants to call a tool
    if assistant_message.tool_calls:
        # Add assistant's tool call request to history
        conversation_history.append(assistant_message)

        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            result = handle_tool_call(tool_call)
            conversation_history.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

        # Second API call - let LLM generate report from tool results
        final_response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2048,
            messages=conversation_history,
        )

        final_message = final_response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": final_message})
        return jsonify({"reply": final_message})

    else:
        # LLM replied directly (e.g., asking for more info)
        reply = assistant_message.content
        conversation_history.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})


# Reset conversation
@app.route("/reset", methods=["POST"])
def reset():
    global conversation_history
    conversation_history = []
    return jsonify({"status": "Conversation reset"})


# ============================================================
# Start the server
# ============================================================
if __name__ == "__main__":
    print("Server running at http://localhost:5000")
    app.run(debug=True, port=5000)
