__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import os
import yaml
import warnings
from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from typing import List
from helper import load_env
import pandas as pd

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

# Streamlit UI
st.set_page_config(page_title="AI Project Planner", layout="wide")
st.title("🚀 CrewAI Project Planner")
st.markdown("Define your project details and let AI generate a structured project plan.")

# Streamlit UI

st.title("🚀 AI-Powered Project Planner")
st.write("This tool helps plan and estimate project timelines using AI agents.")

# User input form
with st.form("project_input_form"):
    project = st.text_input("Project Name", "Website")
    industry = st.text_input("Industry", "Technology")
    project_objectives = st.text_area("Project Objectives", "Create a website for a small business")
    team_members = st.text_area("Team Members", "- John Doe (Project Manager)\n- Jane Doe (Software Engineer)")
    project_requirements = st.text_area("Project Requirements", "- Responsive design\n- Modern UI\n- SEO optimization")
    
    submit = st.form_submit_button("Generate Project Plan")

# Run Crew AI system when user submits
if submit:
    inputs = {
        'project_type': project,
        'project_objectives': project_objectives,
        'industry': industry,
        'team_members': team_members,
        'project_requirements': project_requirements
    }
    
    st.write("⏳ Running AI Agents to generate your project plan...")
    result = crew.kickoff(inputs=inputs)
    st.success("✅ Project Plan Generated!")

    # Display Task Breakdown
    tasks = result.pydantic.dict().get('tasks', [])
    if tasks:
        df_tasks = pd.DataFrame(tasks)
        st.subheader("📌 Task Breakdown")
        st.dataframe(df_tasks)

    # Display Milestones
    milestones = result.pydantic.dict().get('milestones', [])
    if milestones:
        df_milestones = pd.DataFrame(milestones)
        st.subheader("🏆 Project Milestones")
        st.dataframe(df_milestones)
