from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.tool_request import ToolRequest
from app.tools.echo import echo_message
from app.db import SessionLocal, Message

router = APIRouter()

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@router.post("/echo")
async def run_echo(req: ToolRequest):
    return {"result": echo_message(req.message)}

@router.get("/echo2", response_class=HTMLResponse)
async def echo():
    return """
    <html>
        <head>
            <title>Echo Test</title>
        </head>
        <body>
            <h1>👋 Hello from Jenkins FastAPI!</h1>
            <p>This is a test response in HTML.</p>
        </body>
    </html>
    """

@router.get("/game", response_class=HTMLResponse)
async def tap_game() -> str:
    """Serve a tiny tap game that works on mobile browsers."""
    return """
    <html>
        <head>
            <title>Tap Game</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; }
                #tap { font-size: 2em; padding: 1em 2em; }
            </style>
        </head>
        <body>
            <h1>Tap Game</h1>
            <p>Tap the button as many times as you can in 10 seconds!</p>
            <button id="tap" disabled>Tap!</button>
            <div id="score">Score: 0</div>
            <div id="timer"></div>
            <script>
                let score = 0;
                let time = 10;
                const btn = document.getElementById('tap');
                const scoreEl = document.getElementById('score');
                const timerEl = document.getElementById('timer');

                function startGame() {
                    score = 0;
                    time = 10;
                    scoreEl.textContent = 'Score: 0';
                    timerEl.textContent = 'Time: ' + time;
                    btn.disabled = false;
                    const interval = setInterval(() => {
                        time--;
                        timerEl.textContent = 'Time: ' + time;
                        if (time === 0) {
                            clearInterval(interval);
                            btn.disabled = true;
                            timerEl.textContent = "Time's up!";
                        }
                    }, 1000);
                }

                btn.addEventListener('click', () => {
                    score++;
                    scoreEl.textContent = 'Score: ' + score;
                });

                window.onload = startGame;
            </script>
        </body>
    </html>
    """

@router.post("/messages")
async def create_message(req: ToolRequest, db: AsyncSession = Depends(get_db)):
    msg = Message(content=req.message)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return {"id": msg.id, "message": msg.content}

@router.get("/messages/{msg_id}")
async def read_message(msg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).where(Message.id == msg_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"id": msg.id, "message": msg.content}
