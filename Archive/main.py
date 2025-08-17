from fastapi import FastAPI, HTTPException, Form, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer
import json
import logging
import asyncio
from datetime import datetime, timedelta
from pydantic import BaseModel
from google import genai
from google.genai.types import HttpOptions
from prompt import EVAL1_PROMPT, EVAL2_PROMPT, JUDGE_PROMPT, TASK_A_QUESTION_PROMPT, TASK_B_QUESTION_PROMPT
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models import get_db, User, Evaluation
from auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI(
    title=settings.app_name, 
    version=settings.app_version,
    description="AI-powered French language practice tool for TEF Canada exam preparation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Environment configuration
gemini_api_key = settings.google_api_key
debug_mode = settings.debug

# Initialize Gemini client
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        logger.info("✅ Gemini API configured successfully")
    except Exception as e:
        logger.error(f"❌ Failed to configure Gemini API: {e}")
        gemini_api_key = None
else:
    logger.warning("⚠️  GOOGLE_API_KEY not set - running in development mode")

# Global storage for evaluation progress (in production, use Redis or database)
evaluation_progress = {}

def cleanup_old_evaluations():
    """Clean up old evaluation progress data to prevent memory leaks."""
    import time
    current_time = time.time()
    to_remove = []
    
    for eval_id, data in evaluation_progress.items():
        # Remove evaluations older than 1 hour
        if current_time - data.get('created_at', 0) > 3600:
            to_remove.append(eval_id)
    
    for eval_id in to_remove:
        del evaluation_progress[eval_id]

# Pydantic models
class EvaluationRequest(BaseModel):
    task_a_question: str
    task_a_response: str
    task_b_question: str
    task_b_response: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str

class EvaluationResponse(BaseModel):
    id: int
    question: str
    score: float
    feedback: str
    strengths: str
    areas_for_improvement: str
    detailed_errors: str = None
    consolidated_scores: str = None
    cross_task_analysis: str = None
    final_tef_writing_score: int = None
    created_at: str



@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Authentication endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    if user.email:
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        created_at=db_user.created_at.isoformat()
    )

@app.post("/api/auth/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token."""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at.isoformat()
    )

# Protected endpoints
@app.get("/api/questions/generate/task-a")
async def generate_task_a_question():
    """Generate an AI-powered question for Task A (no authentication required)."""
    try:
        question = await call_gemini_model(TASK_A_QUESTION_PROMPT, "Task A Question Generator")
        return {"question": question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Task A question: {str(e)}")

@app.get("/api/questions/generate/task-b")
async def generate_task_b_question():
    """Generate an AI-powered question for Task B (no authentication required)."""
    try:
        question = await call_gemini_model(TASK_B_QUESTION_PROMPT, "Task B Question Generator")
        return {"question": question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Task B question: {str(e)}")

@app.post("/api/evaluate")
async def evaluate_writing(
    request: EvaluationRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Evaluate writing response for both Task A and Task B (requires authentication)."""
    try:
        # Generate unique evaluation ID
        import uuid
        evaluation_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        evaluation_progress[evaluation_id] = {
            "eval1_status": "starting",
            "eval2_status": "waiting", 
            "judge_status": "waiting",
            "current_step": "eval1",
            "overall_progress": 0,
            "completed": False,
            "result": None,
            "error": None,
            "created_at": datetime.utcnow().timestamp() # Add created_at timestamp
        }
        
        # Start background evaluation task
        background_tasks.add_task(
            run_evaluation_background,
            evaluation_id,
            request,
            current_user.id,
            db
        )
        
        return {
            "evaluation_id": evaluation_id,
            "message": "Evaluation started",
            "progress_endpoint": f"/api/evaluate/{evaluation_id}/progress"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.get("/api/evaluate/{evaluation_id}/progress")
async def get_evaluation_progress(evaluation_id: str):
    """Stream evaluation progress updates."""
    # Clean up old evaluations
    cleanup_old_evaluations()
    
    async def progress_stream():
        while True:
            if evaluation_id not in evaluation_progress:
                yield f"data: {json.dumps({'error': 'Evaluation not found'})}\n\n"
                break
                
            progress = evaluation_progress[evaluation_id]
            
            # Send progress update
            yield f"data: {json.dumps(progress)}\n\n"
            
            # If evaluation is completed or failed, end the stream
            if progress["completed"] or progress["error"]:
                break
                
            # Wait before next update
            await asyncio.sleep(0.5)
    
    return StreamingResponse(
        progress_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

async def run_evaluation_background(evaluation_id: str, request: EvaluationRequest, user_id: int, db: Session):
    """Run evaluation in background with progress updates."""
    try:
        progress = evaluation_progress[evaluation_id]
        
        # Evaluate Task A - Evaluator 1
        progress["eval1_status"] = "working"
        progress["current_step"] = "eval1"
        progress["overall_progress"] = 20
        
        task_a_eval1_result = await call_gemini_model(
            EVAL1_PROMPT.format(question=request.task_a_question, response=request.task_a_response),
            "Task A Evaluator 1"
        )
        
        progress["eval1_status"] = "completed"
        progress["overall_progress"] = 40
        
        # Evaluate Task A - Evaluator 2
        progress["eval2_status"] = "working"
        progress["current_step"] = "eval2"
        progress["overall_progress"] = 50
        
        task_a_eval2_result = await call_gemini_model(
            EVAL2_PROMPT.format(question=request.task_a_question, response=request.task_a_response),
            "Task A Evaluator 2"
        )
        
        progress["eval2_status"] = "completed"
        progress["overall_progress"] = 70
        
        # Evaluate Task B - Evaluator 1
        progress["overall_progress"] = 75
        
        task_b_eval1_result = await call_gemini_model(
            EVAL1_PROMPT.format(question=request.task_b_question, response=request.task_b_response),
            "Task B Evaluator 1"
        )
        
        progress["overall_progress"] = 80
        
        # Evaluate Task B - Evaluator 2
        progress["overall_progress"] = 85
        
        task_b_eval2_result = await call_gemini_model(
            EVAL2_PROMPT.format(question=request.task_b_question, response=request.task_b_response),
            "Task B Evaluator 2"
        )
        
        progress["overall_progress"] = 90
        
        # Combine results for final judgment
        progress["judge_status"] = "working"
        progress["current_step"] = "judge"
        progress["overall_progress"] = 95
        
        combined_results = f"Task A - Evaluator 1: {task_a_eval1_result}\n\nTask A - Evaluator 2: {task_a_eval2_result}\n\nTask B - Evaluator 1: {task_b_eval1_result}\n\nTask B - Evaluator 2: {task_b_eval2_result}"
        final_judgment = await call_gemini_model(
            JUDGE_PROMPT.format(
                question=f"Task A: {request.task_a_question}\nTask B: {request.task_b_question}",
                response=f"Task A Response: {request.task_a_response}\nTask B Response: {request.task_b_response}",
                eval1_result=combined_results
            ),
            "Final Judge"
        )
        
        progress["judge_status"] = "completed"
        progress["current_step"] = "completed"
        progress["overall_progress"] = 100
        
        # Parse final judgment to extract score and feedback
        try:
            judgment_data = json.loads(final_judgment)
            
            # Extract the final TEF score from the Judge LLM (this is the ONLY score that matters)
            final_tef_score = judgment_data.get("final_tef_writing_score", 0)
            
            # Ensure the score is within 0-450 range
            final_tef_score = max(0, min(450, final_tef_score))
            
            # Format feedback for better readability using the new schema
            feedback = judgment_data.get("feedback", {})
            if isinstance(feedback, dict):
                # Ensure feedback has the expected structure from new schema
                formatted_feedback = {
                    "content": feedback.get("content", "Feedback non disponible"),
                    "grammar": feedback.get("grammar", "Feedback non disponible"),
                    "organization": feedback.get("organization", "Feedback non disponible"),
                    "overall": feedback.get("overall", "Évaluation générale non disponible")
                }
            else:
                formatted_feedback = {"overall": str(feedback)}
            
            # Extract strengths and areas for improvement
            strengths = judgment_data.get("strengths", [])
            if not isinstance(strengths, list):
                strengths = [str(strengths)] if strengths else []
            
            areas_for_improvement = judgment_data.get("areas_for_improvement", [])
            if not isinstance(areas_for_improvement, list):
                areas_for_improvement = [str(areas_for_improvement)] if areas_for_improvement else []
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            final_tef_score = 0
            formatted_feedback = {"overall": "Erreur lors de l'analyse de l'évaluation"}
            strengths = []
            areas_for_improvement = []
        
        # Save evaluation to database (combining both tasks)
        combined_question = f"Task A: {request.task_a_question}\nTask B: {request.task_b_question}"
        combined_response = f"Task A Response: {request.task_a_response}\nTask B Response: {request.task_b_response}"
        
        db_evaluation = Evaluation(
            user_id=user_id,
            question=combined_question,
            response=combined_response,
            score=final_tef_score,  # Store the TEF score directly
            feedback=json.dumps(formatted_feedback),
            strengths=json.dumps(strengths),
            areas_for_improvement=json.dumps(areas_for_improvement),
            detailed_errors=json.dumps(judgment_data.get("detailed_errors", {})),
            consolidated_scores=json.dumps(judgment_data.get("consolidated_scores", {})),
            cross_task_analysis=json.dumps(judgment_data.get("cross_task_analysis", {})),
            final_tef_writing_score=final_tef_score
        )
        
        db.add(db_evaluation)
        db.commit()
        db.refresh(db_evaluation)
        
        # Store final result - ONLY return the Judge LLM score out of 450
        result = {
            "final_tef_writing_score": final_tef_score,  # This is the ONLY score that matters
            "feedback": formatted_feedback,
            "strengths": strengths,
            "areas_for_improvement": areas_for_improvement,
            "evaluation_id": db_evaluation.id,
            "detailed_errors": judgment_data.get("detailed_errors", {}),
            "consolidated_scores": judgment_data.get("consolidated_scores", {}),
            "cross_task_analysis": judgment_data.get("cross_task_analysis", {})
        }
        
        progress["result"] = result
        progress["completed"] = True
        
    except Exception as e:
        logger.error(f"Background evaluation failed: {str(e)}")
        evaluation_progress[evaluation_id]["error"] = str(e)
        evaluation_progress[evaluation_id]["completed"] = True

@app.get("/api/evaluations", response_model=list[EvaluationResponse])
async def get_user_evaluations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all evaluations for the current user."""
    evaluations = db.query(Evaluation).filter(Evaluation.user_id == current_user.id).order_by(Evaluation.created_at.desc()).all()
    
    return [
        EvaluationResponse(
            id=eval.id,
            question=eval.question,
            score=eval.final_tef_writing_score or eval.score,  # Prioritize TEF score
            feedback=eval.feedback,
            strengths=eval.strengths,
            areas_for_improvement=eval.areas_for_improvement,
            detailed_errors=eval.detailed_errors,
            consolidated_scores=eval.consolidated_scores,
            cross_task_analysis=eval.cross_task_analysis,
            final_tef_writing_score=eval.final_tef_writing_score,
            created_at=eval.created_at.isoformat()
        )
        for eval in evaluations
    ]

@app.get("/api/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific evaluation by ID (only if it belongs to the current user)."""
    evaluation = db.query(Evaluation).filter(
        Evaluation.id == evaluation_id,
        Evaluation.user_id == current_user.id
    ).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    return EvaluationResponse(
        id=evaluation.id,
        question=evaluation.question,
        score=evaluation.final_tef_writing_score or evaluation.score,  # Prioritize TEF score
        feedback=evaluation.feedback,
        strengths=evaluation.strengths,
        areas_for_improvement=evaluation.areas_for_improvement,
        detailed_errors=evaluation.detailed_errors,
        consolidated_scores=evaluation.consolidated_scores,
        cross_task_analysis=evaluation.cross_task_analysis,
        final_tef_writing_score=evaluation.final_tef_writing_score,
        created_at=evaluation.created_at.isoformat()
    )

async def call_gemini_model(prompt: str, evaluator_name: str):
    """Call Google's Gemini model for evaluation."""
    try:
        if not gemini_api_key:
            # Development fallback - return mock response
            print(f"⚠️  Development mode: Mock response for {evaluator_name}")
            return json.dumps({
                "score": 75,
                "feedback": {
                    "content": "Mock feedback for development",
                    "grammar": "Mock grammar feedback",
                    "organization": "Mock organization feedback",
                    "overall": "Mock overall assessment"
                },
                "strengths": ["Mock strength 1", "Mock strength 2"],
                "areas_for_improvement": ["Mock area 1", "Mock area 2"]
            })
        
        # Initialize Gemini client
        client = genai.Client(http_options=HttpOptions(api_version="v1"))
        
        # Call the model
        response = client.models.generate_content(
            model=settings.ai_model_name,
            contents=prompt,
        )
        
        if response.text:
            # Try to parse as JSON first
            try:
                json.loads(response.text)
                return response.text
            except json.JSONDecodeError:
                # If not valid JSON, return as is
                return response.text
        else:
            return f"Error: No response from {evaluator_name}"
            
    except Exception as e:
        print(f"❌ Error calling Gemini model ({evaluator_name}): {str(e)}")
        return f"Error: {str(e)}"

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "gemini_api_configured": bool(gemini_api_key),
        "debug_mode": debug_mode
    }

@app.get("/api/status")
async def status_check():
    """Detailed status check including database connectivity."""
    try:
        # Test database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "application": "TEF AI Practice Tool",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "gemini_api": {
            "configured": bool(gemini_api_key),
            "api_key_set": bool(gemini_api_key)
        },
        "environment": {
            "debug": debug_mode,
            "node_env": "development"  # Could be made configurable if needed
        }
    }

@app.get("/api/config")
async def get_config():
    """Get frontend configuration values."""
    return {
        "writing_time_minutes": settings.writing_time_minutes,
        "app_name": settings.app_name,
        "app_version": settings.app_version
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
