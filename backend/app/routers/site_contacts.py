from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.site_contacts import SiteContacts
from app.models.user import User
from app.schemas.site_contacts import ContactsResponse, ContactsUpdate
from app.security import require_admin

router = APIRouter(prefix="/api/site/contacts", tags=["Контакты сайта"])


@router.get("", response_model=ContactsResponse)
def get_contacts(db: Session = Depends(get_db)):
    contacts = db.get(SiteContacts, 1)
    if contacts is None:
        return ContactsResponse()
    return ContactsResponse.model_validate(contacts).model_copy(update={"configured": True})


@router.put("", response_model=ContactsResponse)
def update_contacts(
    data: ContactsUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
):
    contacts = db.get(SiteContacts, 1)
    if contacts is None:
        contacts = SiteContacts(id=1)
        db.add(contacts)
    for field, value in data.model_dump().items():
        setattr(contacts, field, value)
    try:
        db.commit()
    except IntegrityError:
        # Another administrator may have saved the initial record concurrently.
        db.rollback()
        contacts = db.get(SiteContacts, 1)
        if contacts is None:
            raise
        for field, value in data.model_dump().items():
            setattr(contacts, field, value)
        db.commit()
    db.refresh(contacts)
    return ContactsResponse.model_validate(contacts).model_copy(update={"configured": True})
