from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.site_about import SiteAbout
from app.schemas.site_about import AboutResponse, AboutUpdate
from app.security import require_admin

router = APIRouter(prefix="/api/site/about", tags=["О нас"])
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "static" / "uploads" / "about"
MAX_IMAGE_SIZE = 10 * 1024 * 1024
DEFAULT_ABOUT = {
    "title": "Мебель для вашего дома",
    "blocks": [{"type": "text", "text": "## Индивидуальное решение начинается с ваших пожеланий\n\nПосмотрите проекты в каталоге и расскажите, какую мебель вы представляете в своём доме. В заявке можно указать размеры, материал, цвет и необходимость замера.\n\n## Как обсудить проект\n\n1. Выберите кухню, шкаф или другое решение из каталога.\n2. Расскажите о размерах и деталях, которые важны для вас.\n3. Оставьте удобное время для обратной связи."}],
}


@router.get("", response_model=AboutResponse)
def get_about(db: Session = Depends(get_db)):
    page = db.get(SiteAbout, 1)
    if page is None:
        return {**DEFAULT_ABOUT, "configured": False}
    return {"title": page.title, "blocks": page.blocks, "configured": True}


@router.put("", response_model=AboutResponse)
def publish_about(data: AboutUpdate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    for block in data.blocks:
        if block.type == "image" and not (UPLOAD_ROOT / block.image_url.rsplit("/", 1)[1]).is_file():
            raise HTTPException(400, "Фотография не найдена. Загрузите её заново.")
    page = db.get(SiteAbout, 1)
    if page is None:
        page = SiteAbout(id=1)
        db.add(page)
    page.title = data.title
    page.blocks = [block.model_dump() for block in data.blocks]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        page = db.get(SiteAbout, 1)
        if page is None:
            raise
        page.title = data.title
        page.blocks = [block.model_dump() for block in data.blocks]
        db.commit()
    return {**data.model_dump(), "configured": True}


@router.post("/images", status_code=201)
async def upload_image(file: UploadFile = File(...), _admin=Depends(require_admin)):
    try:
        content = await file.read(MAX_IMAGE_SIZE + 1)
    finally:
        await file.close()
    if not content or len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(400, "Выберите непустое изображение размером до 10 МБ.")
    # Determine the extension from bytes, never from the supplied filename.
    if content.startswith(b"\xff\xd8\xff"):
        extension = "jpg"
    elif content.startswith(b"\x89PNG\r\n\x1a\n"):
        extension = "png"
    elif content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        extension = "webp"
    else:
        raise HTTPException(400, "Допустимы фотографии JPG, PNG и WebP.")
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.{extension}"
    (UPLOAD_ROOT / filename).write_bytes(content)
    return {"image_url": f"/static/uploads/about/{filename}"}
