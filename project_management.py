import pandas as pd


# --------------------------------------------------
# PROJECT DETAILS
# --------------------------------------------------

PROJECT_NAME = "Smart Cosmetic Product Management and Customer Opinion Analytics System"

PROJECT_DURATION = "16 Weeks"

PROJECT_MANAGER = "Project Manager"


# --------------------------------------------------
# WORK BREAKDOWN STRUCTURE
# --------------------------------------------------

def get_wbs():

    data = {
        "WBS ID": [
            "1",
            "1.1",
            "1.2",
            "2",
            "2.1",
            "2.2",
            "3",
            "3.1",
            "3.2",
            "3.3",
            "4",
            "4.1",
            "4.2",
            "5",
            "5.1",
            "5.2",
            "6"
        ],

        "Task": [
            "Project Planning",
            "Requirement Analysis",
            "Project Scheduling",
            "System Development",
            "Database Development",
            "Dashboard Development",
            "ASTMA Module",
            "Text Preprocessing",
            "Sentiment Analysis",
            "Opinion Mining",
            "Enterprise System Module",
            "Product Management",
            "Review Management",
            "Testing",
            "Functional Testing",
            "Integration Testing",
            "Project Deployment"
        ],

        "Subject": [
            "ITPM",
            "ITPM",
            "ITPM",
            "ES + ASTMA",
            "ES",
            "ES",
            "ASTMA",
            "ASTMA",
            "ASTMA",
            "ASTMA",
            "ES",
            "ES",
            "ES + ASTMA",
            "ITPM",
            "ITPM",
            "ITPM",
            "ITPM"
        ]
    }

    return pd.DataFrame(data)


# --------------------------------------------------
# PROJECT SCHEDULE
# --------------------------------------------------

def get_schedule():

    data = {
        "Task": [
            "Requirement Analysis",
            "System Design",
            "Database Development",
            "Text Preprocessing",
            "Sentiment Analysis",
            "Opinion Mining",
            "Product Management",
            "Review Management",
            "Dashboard Development",
            "System Testing",
            "Final Documentation",
            "Deployment"
        ],

        "Start Week": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            12,
            14,
            16
        ],

        "Duration (Weeks)": [
            1,
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            3,
            2,
            2,
            1
        ],

        "Responsible": [
            "Project Team",
            "Project Team",
            "ES Team",
            "ASTMA Team",
            "ASTMA Team",
            "ASTMA Team",
            "ES Team",
            "ES + ASTMA Team",
            "Development Team",
            "Testing Team",
            "Project Manager",
            "Project Team"
        ]
    }

    return pd.DataFrame(data)


# --------------------------------------------------
# MILESTONES
# --------------------------------------------------

def get_milestones():

    data = {
        "Milestone": [
            "Requirements Completed",
            "System Design Completed",
            "Database Completed",
            "ASTMA Module Completed",
            "ES Module Completed",
            "Dashboard Completed",
            "Testing Completed",
            "Final Project Completed"
        ],

        "Target Week": [
            1,
            2,
            3,
            6,
            10,
            12,
            14,
            16
        ],

        "Status": [
            "Completed",
            "Completed",
            "Completed",
            "Completed",
            "In Progress",
            "In Progress",
            "Pending",
            "Pending"
        ]
    }

    return pd.DataFrame(data)


# --------------------------------------------------
# RESOURCE PLAN
# --------------------------------------------------

def get_resources():

    data = {
        "Resource": [
            "Project Manager",
            "Python Developer",
            "Database Developer",
            "ASTMA/NLP Developer",
            "UI/Dashboard Developer",
            "Testing Resource"
        ],

        "Role": [
            "Planning & Monitoring",
            "Application Development",
            "Database Management",
            "Text & Sentiment Analysis",
            "Dashboard Development",
            "Testing & Validation"
        ],

        "Allocation": [
            "20%",
            "80%",
            "50%",
            "70%",
            "60%",
            "40%"
        ]
    }

    return pd.DataFrame(data)


# --------------------------------------------------
# COST ESTIMATION
# --------------------------------------------------

def get_cost_estimation():

    data = {
        "Cost Component": [
            "Software Development",
            "Database & Cloud",
            "Testing",
            "Documentation",
            "Miscellaneous"
        ],

        "Estimated Cost (₹)": [
            25000,
            10000,
            8000,
            5000,
            7000
        ]
    }

    return pd.DataFrame(data)


# --------------------------------------------------
# RISK REGISTER
# --------------------------------------------------

def get_risks():

    data = {
        "Risk": [
            "Poor review data quality",
            "Incorrect sentiment classification",
            "Database failure",
            "Project schedule delay",
            "Integration problems",
            "Insufficient testing"
        ],

        "Probability": [
            "Medium",
            "Medium",
            "Low",
            "Medium",
            "Medium",
            "Low"
        ],

        "Impact": [
            "High",
            "Medium",
            "High",
            "High",
            "Medium",
            "Medium"
        ],

        "Mitigation": [
            "Clean and validate review data",
            "Test NLP model with sample reviews",
            "Maintain database backup",
            "Track schedule and milestones",
            "Test modules independently before integration",
            "Prepare test cases"
        ]
    }

    return pd.DataFrame(data)


# --------------------------------------------------
# PROJECT SUMMARY
# --------------------------------------------------

def get_project_summary():

    return {
        "Project Name": PROJECT_NAME,
        "Duration": PROJECT_DURATION,
        "Project Manager": PROJECT_MANAGER,
        "Main Subjects": "ES + ITPM + ASTMA",
        "Technology": "Python, Streamlit, SQLite, NLP, VADER"
    }