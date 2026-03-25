from platform import architecture
import json
from openai import OpenAI
import n

# step 1: connect to OpenAI API
client = OpenAI(
    # here is your API key
    api_key="xxxxxx"
)


def connect_OpenAI():
    pass
    # response = client.chat.completions.create(
    #     model="gpt-4o", max_tokens=1024, messages=[{"role": "user", "content": "hi"}]
    # )

    # print(response.choices[0].message.content)


# step 2: collect project requirements
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
        "project": project,
        "architecture": architecture,
        "service_model": service_model,
        "deployment_model": deployment_model,
        "explanation": explanation,
        "scores": scores,
    }


# step 3
tools = [
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


# step 4
def handle_tool_call(tool_call):

    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "analyze_project":
        result = analyze_project(**arguments)
        return json.dumps(result, indent=2)
    else:
        return json.dumps({"error": f"Unknown function: {function_name}"})


# step 5
def run_agent():
    """
    Agent 主循环：
    1. 用户输入自然语言描述
    2. 发送给 LLM（带工具描述）
    3. 如果 LLM 想调用工具 → 执行工具 → 把结果返回给 LLM
    4. LLM 根据工具结果生成最终回复
    5. 如果 LLM 直接回复（比如追问信息）→ 显示回复
    6. 循环直到用户输入 quit
    """
    print("=" * 60)
    print("  AI Architecture Recommender Agent")
    print("  Describe your project and I'll recommend an architecture.")
    print("  Type 'quit' to exit.")
    print("=" * 60)

    # system prompt: 告诉 LLM 它的角色和行为规则
    system_message = {
        "role": "system",
        "content": (
            "You are an AI architecture consultant. "
            "The user will describe their AI project requirements in natural language. "
            "Your job is to: "
            "1. Extract the 9 required parameters from the user's description. "
            "2. If any parameter is missing or unclear, ask the user for clarification. "
            "3. Once you have all parameters, call the analyze_project tool. "
            "4. Present the results in a clear, professional report format. "
            "Always respond in the same language the user uses."
        ),
    }

    # 对话历史：保存所有消息，让 LLM 有上下文记忆
    conversation_history = [system_message]

    while True:
        # 第1步：获取用户输入
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if not user_input:
            continue

        # 第2步：把用户消息加入对话历史
        conversation_history.append({"role": "user", "content": user_input})

        # 第3步：发送给 LLM（带工具描述）
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2048,
            messages=conversation_history,
            tools=tools,
        )

        # 获取 LLM 的回复
        assistant_message = response.choices[0].message

        # 第4步：检查 LLM 是否想调用工具
        if assistant_message.tool_calls:
            # LLM 决定调用工具了！
            # 先把 LLM 的回复（包含工具调用请求）加入历史
            conversation_history.append(assistant_message)

            # 执行每个工具调用
            for tool_call in assistant_message.tool_calls:
                print(f"\n[Agent is calling tool: {tool_call.function.name}...]")
                result = handle_tool_call(tool_call)

                # 把工具执行结果加入对话历史
                conversation_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

            # 第5步：把工具结果发回给 LLM，让它生成最终报告
            final_response = client.chat.completions.create(
                model="gpt-4o",
                max_tokens=2048,
                messages=conversation_history,
            )

            final_message = final_response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": final_message})
            print(f"\nAssistant: {final_message}")

        else:
            # LLM 没有调用工具，直接回复（可能是在追问缺少的参数）
            reply = assistant_message.content
            conversation_history.append({"role": "assistant", "content": reply})
            print(f"\nAssistant: {reply}")


def main():
    # connect_OpenAI()
    pass


if __name__ == "__main__":
    run_agent()
