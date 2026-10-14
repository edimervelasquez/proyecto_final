from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.repositories.produccion_repository import ProduccionRepository


def validar_usuario_operativo(db: Session, id_usuario: int):
    usuario = ProduccionRepository.obtener_usuario(db, id_usuario)
    if not usuario or (usuario.estado or "").upper() not in ("ACTIVO", "APROBADO"):
        raise HTTPException(
            status_code=403,
            detail="Se requiere una cuenta activa para esta operación.",
        )
    if usuario.id_rol not in (1, 2):
        raise HTTPException(
            status_code=403,
            detail="Solo administradores y trabajadores pueden realizar esta operación.",
        )
    return usuario
