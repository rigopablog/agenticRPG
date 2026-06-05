import os
import sys
import json
import asyncio
import requests
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq

sys.path.insert(0, str(Path(__file__).parent))          # app/ → agent_defs
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))  # python/ → crewai etc.
load_dotenv(Path(__file__).parent.parent / ".env")

from agent_defs import AGENTS, AGENTS_BY_ID

app = FastAPI(title="Agents Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://rpgdevelopment.com",
        "https://www.rpgdevelopment.com",
        "https://web-production-07e84.up.railway.app",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


class RunRequest(BaseModel):
    agent_id: str
    task: str
    context: str = ""


class OrchestrationStep(BaseModel):
    agent_id: str
    task: str


class OrchestrationRequest(BaseModel):
    steps: list[OrchestrationStep]
    mode: str = "sequential"  # sequential | parallel


@app.get("/", response_class=HTMLResponse)
async def root():
    html = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/api/agents")
def get_agents():
    return AGENTS


@app.post("/api/run/stream")
async def run_agent_stream(req: RunRequest):
    agent = AGENTS_BY_ID.get(req.agent_id)
    if not agent:
        return {"error": "Agent not found"}

    user_content = req.task
    if req.context:
        user_content = f"Contexto previo:\n{req.context}\n\nTarea actual:\n{req.task}"

    def generate():
        stream = groq_client.chat.completions.create(
            model=MODEL,
            max_tokens=4000,
            stream=True,
            messages=[
                {"role": "system", "content": agent["system"]},
                {"role": "user", "content": user_content},
            ],
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {json.dumps({'content': delta})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                              headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/orchestrate/stream")
async def orchestrate_stream(req: OrchestrationRequest):
    async def generate():
        if req.mode == "sequential":
            context = ""
            for i, step in enumerate(req.steps):
                agent = AGENTS_BY_ID.get(step.agent_id)
                if not agent:
                    continue

                header = json.dumps({
                    "type": "step_start",
                    "step": i + 1,
                    "total": len(req.steps),
                    "agent": agent["name"],
                    "icon": agent["icon"],
                })
                yield f"data: {header}\n\n"

                user_content = step.task
                if context:
                    user_content = f"Contexto del paso anterior:\n{context}\n\nTu tarea:\n{step.task}"

                step_output = ""
                loop = asyncio.get_event_loop()

                def run_sync():
                    result = []
                    stream = groq_client.chat.completions.create(
                        model=MODEL,
                        max_tokens=2000,
                        stream=True,
                        messages=[
                            {"role": "system", "content": agent["system"]},
                            {"role": "user", "content": user_content},
                        ],
                    )
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            result.append(delta)
                    return "".join(result)

                step_output = await loop.run_in_executor(None, run_sync)
                context = step_output

                yield f"data: {json.dumps({'type': 'step_result', 'step': i+1, 'content': step_output})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        elif req.mode == "parallel":
            results = {}

            async def run_agent(step, idx):
                agent = AGENTS_BY_ID.get(step.agent_id)
                if not agent:
                    return

                loop = asyncio.get_event_loop()

                def run_sync():
                    out = []
                    stream = groq_client.chat.completions.create(
                        model=MODEL,
                        max_tokens=2000,
                        stream=True,
                        messages=[
                            {"role": "system", "content": agent["system"]},
                            {"role": "user", "content": step.task},
                        ],
                    )
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            out.append(delta)
                    return "".join(out)

                output = await loop.run_in_executor(None, run_sync)
                results[idx] = {"agent": agent["name"], "icon": agent["icon"], "content": output}

            tasks = [run_agent(step, i) for i, step in enumerate(req.steps)]
            await asyncio.gather(*tasks)

            for idx in sorted(results.keys()):
                r = results[idx]
                yield f"data: {json.dumps({'type': 'parallel_result', 'step': idx+1, **r})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                              headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    import uvicorn
    print("\nAgents Hub corriendo en http://localhost:8000\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
