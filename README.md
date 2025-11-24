# AI Interview Practice Partner

## Overview  
AI Interview Practice Partner is a web‑based application designed to help users prepare for job interviews by simulating interview sessions and providing feedback on their responses.

## Features  
- Allows users to select or specify a job role and domain for the interview.  
- Simulates a structured interview session with questions and responses.  
- Records or processes user answers (text/audio) and generates feedback for improvement.  
- Provides a history of sessions for review and self‐reflection.  
- Frontend + backend architecture for managing user sessions and generating interview flow.

## Repository Structure  
/backend # API, business logic, data handling
/frontend # User interface, session flows
/demo_scenarios.md # Sample roles/questions/flows to test
requirements.txt # Backend dependencies
.gitignore
README.md # This file


## Tech Stack  
- Backend: Python (Flask / FastAPI)  
- Frontend: HTML / CSS / JavaScript (or React/Vue)  
- Data: Session state, transcripts, feedback logic  
- AI/ML: For generating questions and feedback (using LLMs or rule‑based system)  
- Deployment: Local or cloud (as configured)

## Setup & Installation  
### Backend  
1. Clone the repository.  
   ```bash
   git clone https://github.com/Kanisha18/AI_Interview_Practice_Partner.git  
   cd AI_Interview_Practice_Partner/backend  

2. Create a virtual environment and activate it.
    python3 -m venv venv  
    source venv/bin/activate  # Windows: venv\Scripts\activate  

3. Install dependencies.
    pip install -r ../requirements.txt  

4. Start the backend server.
    uvicorn main:app --reload  # or `python app.py` depending on setup  

### Frontend

1. Navigate to the frontend directory.
    cd ../frontend  

2. If using npm/yarn, install dependencies.
    npm install  
    npm start  

3. Open your browser and go to http://localhost:3000 (or configured port).

