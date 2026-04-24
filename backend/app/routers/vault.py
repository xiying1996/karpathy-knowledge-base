from fastapi import APIRouter

from app.models import VaultFile, VaultListResponse
from app.services.vault_reader import VaultReader

router = APIRouter()
vault_reader = VaultReader()


@router.get("/vault/files", response_model=VaultListResponse)
def list_vault_files():
    notes = vault_reader.list_notes()
    files = [
        VaultFile(
            id=n["id"],
            path=n["id"],
            title=n["title"],
            tags=n.get("tags", []),
            modified=n.get("modified"),
            excerpt=n.get("excerpt", ""),
        )
        for n in notes
    ]
    return VaultListResponse(files=files, total=len(files))