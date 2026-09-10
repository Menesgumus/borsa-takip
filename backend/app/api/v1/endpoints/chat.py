from fastapi import APIRouter, HTTPException

router = APIRouter()

# Keep minimal tombstone router only to guarantee 410 semantics.
# Do not:
# - generate a Mentor response
# - create ChatThread
# - create ChatMessage
# - invoke any LLM

@router.post("/threads")
async def create_thread():
    raise HTTPException(status_code=410, detail={"code": "MENTOR_REMOVED", "message": "Mentor özelliği bu uygulamadan kaldırıldı."})

@router.get("/threads/{thread_id}")
async def get_thread(thread_id: int):
    raise HTTPException(status_code=410, detail={"code": "MENTOR_REMOVED", "message": "Mentor özelliği bu uygulamadan kaldırıldı."})

@router.post("/threads/{thread_id}/messages")
async def send_message(thread_id: int):
    raise HTTPException(status_code=410, detail={"code": "MENTOR_REMOVED", "message": "Mentor özelliği bu uygulamadan kaldırıldı."})
