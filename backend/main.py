from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routers.adressee_router import router as adressee_router
from routers.api_router import router as api_router
from routers.area_router import router as area_router
from routers.emplyee_router import router as emplyee_router
from routers.faximili_router import router as faximili_router
from routers.letter_history_router import router as letter_history_router
from routers.notebook_router import router as notebook_router
from routers.organization_router import router as organization_router
from routers.signer_router import router as signer_router
from routers.template_router import router as template_router
from routers.users_router import router as users_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/preview", StaticFiles(directory="./static/preview"), name="preview")
app.mount("/static/converted_files", StaticFiles(directory="./static/converted_files"), name="converted_files")
app.mount("/static/templates", StaticFiles(directory="./static/templates"), name="templates")

app.include_router(adressee_router)
app.include_router(api_router)
app.include_router(area_router)
app.include_router(emplyee_router)
app.include_router(faximili_router)
app.include_router(letter_history_router)
app.include_router(notebook_router)
app.include_router(organization_router)
app.include_router(signer_router)
app.include_router(template_router)
app.include_router(users_router)


@app.get("/images/{image_path:path}")
async def get_image(image_path: str):
    image_full_path = os.path.join("static", image_path)
    print(image_full_path)
    if not os.path.exists(image_full_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_full_path)
