from os import system
import sys


def get_valid_input(prompt, valid_options):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in valid_options:
            return user_input
        else:
            print(f"Invalid input. Please choose from: {', '.join(valid_options)}")


def collection_project_requirements():
    print("===== Welcome to the Collection Project! ======")
    print("===== Please provide the following information: =====")

    project = {}
    project["name"] = input("Project Name: ").strip()
    project["ai_workload"] = get_valid_input(
        "AI Workload (nlp, vision, prediction, expert_system): ",
        ["nlp", "vision", "prediction", "expert_system"],
    )
    project["system_size"] = get_valid_input(
        "System Size (small, medium, large): ", ["small", "medium", "large"]
    )
    project["scalability"] = get_valid_input(
        "Scalability (low, medium, high): ", ["low", "medium", "high"]
    )
    project["real_time"] = get_valid_input(
        "Real-time Requirement (yes, no): ", ["yes", "no"]
    )
    project["budget"] = get_valid_input(
        "Budget (low, medium, high): ", ["low", "medium", "high"]
    )
    project["cloud_expertise"] = get_valid_input(
        "Cloud Expertise (low, medium, high): ", ["low", "medium", "high"]
    )
    project["data_sensitivity"] = get_valid_input(
        "Data Sensitivity (low, medium, high): ", ["low", "medium", "high"]
    )
    project["deployment_preference"] = get_valid_input(
        "Deployment Preference (public, private, hybrid, community): ",
        ["public", "private", "hybrid", "community"],
    )

    return project


def recommend_architecture(project):
    """
    Recommends an AI architecture based on the project requirements.
    """
    scores = {
        "monolithic": 0,
        "layered": 0,
        "microservices": 0,
        "serverless": 0,
        "event_driven": 0,
    }

    if project["system_size"] == "small":
        scores["monolithic"] += 3
        scores["layered"] += 2
        scores["serverless"] += 2
    elif project["system_size"] == "medium":
        scores["layered"] += 3
        scores["microservices"] += 2
        scores["serverless"] += 1
    else:
        scores["microservices"] += 4
        scores["event_driven"] += 3
        scores["serverless"] += 1

    if project["scalability"] == "high":
        scores["microservices"] += 4
        scores["event_driven"] += 3
        scores["serverless"] += 3
    elif project["scalability"] == "medium":
        scores["layered"] += 2
        scores["microservices"] += 2
    else:
        scores["monolithic"] += 2

    if project["real_time"] == "yes":
        scores["event_driven"] += 3
        scores["serverless"] += 2
    else:
        scores["monolithic"] += 1
        scores["layered"] += 1

    if project["budget"] == "low":
        scores["monolithic"] += 3
        scores["layered"] += 2
    elif project["budget"] == "medium":
        scores["layered"] += 2
        scores["microservices"] += 1
    else:
        scores["microservices"] += 2
        scores["event_driven"] += 1

    if project["ai_workload"] in ["nlp", "vision"]:
        scores["event_driven"] += 1
        scores["microservices"] += 2
    elif project["ai_workload"] == "prediction":
        scores["layered"] += 2
        scores["serverless"] += 1
    else:
        scores["monolithic"] += 1
        scores["layered"] += 2
    best_Architecture = max(scores, key=scores.get)
    return best_Architecture, scores


def recommend_cloud_service_model(project, architecture):
    """recommend saas paas iaas"""
    if architecture == "serverless":
        return "paas"
    if architecture == "microservices" and project["cloud_expertise"] == "high":
        return "iaas"
    if project["budget"] == "low" and project["cloud_expertise"] == "low":
        return "saas"
    if project["ai_workload"] in ["nlp", "vision"]:
        return "paas"
    return "iaas"


def recommend_deployment_model(project, architecture):
    """recommend cloud deployment model"""
    if project["data_sensitivity"] == "high":
        if project["deployment_preference"] == "hybrid":
            return "hybrid cloud"
        return "private cloud"
    else:
        if project["deployment_preference"] == "community":
            return "community cloud"
        elif project["deployment_preference"] == "hybrid":
            return "hybrid cloud"
        else:
            return "public cloud"


def bulid_explanation(project, architecture, service_model, deployment_model):
    """build explanation for the recommendation"""

    reason = []

    if architecture == "serverless":
        reason.append(
            "Serverless architecture is recommended for its scalability and cost-effectiveness, especially for projects with variable workloads."
        )
    elif architecture == "event_driven":
        reason.append(
            "Event-driven architecture is recommended for its real-time processing, especially for projects with high-frequency data."
        )
    elif architecture == "microservices":
        reason.append(
            "Microservices architecture is recommended for its modularity, scalability, and flexibility, especially for projects with complex workloads."
        )
    elif architecture == "layered":
        reason.append(
            "Layered architecture is recommended for its modularity, flexibility, and reusability, especially for projects with complex workloads."
        )
    elif architecture == "monolithic":
        reason.append(
            "Monolithic architecture is recommended for its simplicity and ease of development, especially for small projects with limited scalability requirements."
        )

    if service_model == "saas":
        reason.append(
            "SaaS is recommended for its ease of use and low maintenance, especially for projects with limited cloud expertise and budget."
        )
    elif service_model == "paas":
        reason.append(
            "PaaS is recommended for its flexibility, scalability, and cost-effectiveness, especially for projects with variable workloads."
        )
    else:
        reason.append(
            "IaaS is recommended for its scalability, flexibility, and cost-effectiveness, especially for projects with high data sensitivity and high-frequency data."
        )

    reason.append(
        f"The {deployment_model} deployment model is recommended for its data sensitivity, security, and cost-effectiveness, especially for projects with high data sensitivity."
    )

    return " ".join(reason)


def diplay_result(
    project, architecture, scores, service_model, deployment_model, explanation
):
    """display the recommendation result"""

    print("====== project summary =======")
    for key, value in project.items():
        print(f"{key.replace('_','').title()}: {value}")

    print("\n====== architecture score =======")
    for arch, score in scores.items():
        print(f"{arch.title()}: {score}")

    print("\n====== recommendation =======")
    print(f"Architecture: {architecture.title()}")
    print(f"Service Model: {service_model.title()}")
    print(f"Deployment Model: {deployment_model.title()}")

    print("\n====== explanation =======")
    print(explanation)


def main():
    project = collection_project_requirements()
    architecture, scores = recommend_architecture(project)
    service_model = recommend_cloud_service_model(project, architecture)
    deployment_model = recommend_deployment_model(project, architecture)
    explanation = bulid_explanation(
        project, architecture, service_model, deployment_model
    )
    diplay_result(
        project, architecture, scores, service_model, deployment_model, explanation
    )


if __name__ == "__main__":
    main()
    input("Press Enter key to exit...")
