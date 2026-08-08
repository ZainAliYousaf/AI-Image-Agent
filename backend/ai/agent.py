from ai.planner import create_plan
from ai.router import execute_plan


def run_agent(user_request, image_paths):

    # Create AI execution plan
    plan = create_plan(user_request)

    # Execute the plan
    result_files = execute_plan(
        plan,
        image_paths
    )

    return {
        "plan": plan,
        "files": result_files
    }