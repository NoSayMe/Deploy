from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.tool_request import ToolRequest
from app.tools.echo import echo_message
from app.db import SessionLocal, Message, HighScore

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
            <button id="start">Start</button>
            <button id="tap" disabled>Tap!</button>
            <button id="refresh" style="display:none;">Play Again</button>
            <div id="score">Score: 0</div>
            <div id="highscore">High Score: 0</div>
            <div id="timer"></div>
            <script>
                let score = 0;
                let time = 10;
                const btn = document.getElementById('tap');
                const startBtn = document.getElementById('start');
                const refreshBtn = document.getElementById('refresh');
                const scoreEl = document.getElementById('score');
                const highEl = document.getElementById('highscore');
                const timerEl = document.getElementById('timer');

                async function fetchHighscore() {
                    const res = await fetch('/tools/game/highscore');
                    if (res.ok) {
                        const data = await res.json();
                        highEl.textContent = 'High Score: ' + data.highscore;
                    }
                }

                function startGame() {
                    score = 0;
                    time = 10;
                    scoreEl.textContent = 'Score: 0';
                    timerEl.textContent = 'Time: ' + time;
                    btn.disabled = false;
                    startBtn.style.display = 'none';
                    refreshBtn.style.display = 'none';
                    const interval = setInterval(async () => {
                        time--;
                        timerEl.textContent = 'Time: ' + time;
                        if (time === 0) {
                            clearInterval(interval);
                            btn.disabled = true;
                            timerEl.textContent = "Time's up!";
                            refreshBtn.style.display = 'inline-block';
                            startBtn.style.display = 'inline-block';
                            try {
                                const res = await fetch('/tools/game/highscore', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ score })
                                });
                                if (res.ok) {
                                    const data = await res.json();
                                    highEl.textContent = 'High Score: ' + data.highscore;
                                    if (data.new_record) {
                                        alert('New high score!');
                                    }
                                }
                            } catch (e) {
                                console.error(e);
                            }
                        }
                    }, 1000);
                }

                btn.addEventListener('click', () => {
                    score++;
                    scoreEl.textContent = 'Score: ' + score;
                });

                refreshBtn.addEventListener('click', startGame);
                startBtn.addEventListener('click', startGame);

                window.onload = () => { fetchHighscore(); };
            </script>
        </body>
    </html>
    """


@router.get("/game/highscore")
async def get_highscore(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HighScore))
    hs = result.scalar_one()
    return {"highscore": hs.score}


@router.post("/game/highscore")
async def post_highscore(data: dict, db: AsyncSession = Depends(get_db)):
    score = int(data.get("score", 0))
    result = await db.execute(select(HighScore))
    hs = result.scalar_one()
    new_record = False
    if score > hs.score:
        hs.score = score
        new_record = True
        await db.commit()
    return {"highscore": hs.score, "new_record": new_record}

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
