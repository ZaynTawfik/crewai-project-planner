import streamlit as st
import os
import yaml
import warnings
from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from typing import List
from helper import load_env

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_env()

# Set OpenAI model (Update with your model choice)
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'

# Load configurations from YAML files
def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

agents_config = load_yaml('config/agents.yaml')
tasks_config = load_yaml('config/tasks.yaml')

# Define structured output models
class TaskEstimate(BaseModel):
    task_name: str = Field(..., description="Name of the task")
    estimated_time_hours: float = Field(..., description="Estimated time to complete the task in hours")
    required_resources: List[str] = Field(..., description="List of resources required to complete the task")

class Milestone(BaseModel):
    milestone_name: str = Field(..., description="Name of the milestone")
    tasks: List[str] = Field(..., description="List of task IDs associated with this milestone")

class ProjectPlan(BaseModel):
    tasks: List[TaskEstimate] = Field(..., description="List of tasks with their estimates")
    milestones: List[Milestone] = Field(..., description="List of project milestones")


# Streamlit UI
st.title("🚀 CrewAI Project Planner")
st.markdown("Define your project details and let AI generate a structured project plan.")

# User Inputs
project = st.text_input("Project Type", "Website")
industry = st.text_input("Industry", "Technology")
project_objectives = st.text_area("Project Objectives", "Create a website for a small business")
team_members = st.text_area("Team Members", "- John Doe (PM)\n- Jane Doe (Developer)")
project_requirements = st.text_area("Project Requirements", "- Responsive design\n- SEO Optimization")

# Button to generate plan
if st.button("Generate Project Plan"):
    with st.spinner("AI is generating your project plan..."):

        # Create agents
        project_planning_agent = Agent(config=agents_config['project_planning_agent'])
        estimation_agent = Agent(config=agents_config['estimation_agent'])
        resource_allocation_agent = Agent(config=agents_config['resource_allocation_agent'])

        # Create tasks
        task_breakdown = Task(config=tasks_config['task_breakdown'], agent=project_planning_agent)
        time_resource_estimation = Task(config=tasks_config['time_resource_estimation'], agent=estimation_agent)
        resource_allocation = Task(config=tasks_config['resource_allocation'], agent=resource_allocation_agent, output_pydantic=ProjectPlan)

        # Create Crew
        crew = Crew(
            agents=[project_planning_agent, estimation_agent, resource_allocation_agent],
            tasks=[task_breakdown, time_resource_estimation, resource_allocation],
            verbose=True
        )

        # Execute Crew
        result = crew.kickoff()

        # Display Results
        st.subheader("📋 Generated Project Plan")
        st.write(result.json(indent=2))

