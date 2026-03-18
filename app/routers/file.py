from fastapi import  UploadFile, File, status, HTTPException,Depends, APIRouter,Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func

from ..database import get_async_db
from .. import models,schemas, storage
from ..config import settings



router = APIRouter()



@router.post("/upload_file", status_code=status.HTTP_201_CREATED,response_model=schemas.FileMetadata)
async def upload_file(file:UploadFile=File(...),db:AsyncSession=Depends(get_async_db)):
    """
    Upload a file and store its metadata in the database.
    The file is stored using Obstore.
    """
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    try:
        file_metadata = await storage.store_file(file,settings.default_store_type)
    except Exception as e:
        print(f"Error storing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store file: {e}")
   
    new_file_entry = models.File(**file_metadata)
    db.add(new_file_entry)
    await db.commit()
    await db.refresh(new_file_entry)
    return  new_file_entry



@router.get("/files",response_model=schemas.Page[schemas.FileMetadata])
async def get_files(db:AsyncSession=Depends(get_async_db),limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),):
    """
    Retrieve metadata of all files from the database.
    """
    total = await db.scalar(
        select(func.count()).select_from(models.File)
    )

    stmt = select(models.File) \
          .limit(limit) \
          .offset(offset)

    result = await db.execute(stmt)
    files = result.scalars().all()

    return {
        "items": files,
        "total": total,
        "limit": limit,
        "offset": offset,
    }



@router.get("/files/{file_id}/metadata",response_model=schemas.FileMetadata)
async def get_file(file_id:int,db:AsyncSession=Depends(get_async_db)):
    """
    Get the metadata of a file from the storage for a given file ID.

    """
    stmt = select(models.File).where(models.File.id == file_id)
    file_metadata = (await db.execute(stmt)).scalars().first()
    if not file_metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"File with {file_id} not found")
    return file_metadata




@router.get("/files/{file_id}/data")
async def get_file_content(file_id:int,db:AsyncSession=Depends(get_async_db)):
    """
    Get the content of a file from the storage for a given file ID.
    First, it fetches the filename from the `files` table, which contains
    metadata of all uploaded files.
    """
    stmt = select(models.File).where(models.File.id == file_id)
    file_metadata = (await db.execute(stmt)).scalars().first()

    return StreamingResponse(
       storage.stream_csv_as_json(file_metadata.filename,settings.default_store_type),
        media_type="application/x-ndjson",
        headers={
        "Content-Disposition": "attachment; filename=data.ndjson"
    })



    
   



