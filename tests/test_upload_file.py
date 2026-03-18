import pytest
import obstore
from app.storage import STORE_CACHE
from app.config import settings
from app import models
from app.storage import get_store
from sqlalchemy import select





@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filename,csv_content",
    [
        ("genes1.csv", b"gene_id,gene_name,chromosome\n1,BRCA1,17\n2,TP53,17"),
        ("genes2.csv", b"gene_id,gene_name,chromosome\n3,EGFR,7\n4,VEGFA,6"),
        ("genes3.csv", b"gene_id,gene_name,chromosome\n5,MYC,8\n6,APOE,19"),
    ]
)
async def test_upload_csv_local_store_creates_metadata(async_test_client,get_test_db_session,create_store,filename,csv_content):
    """
    Test POST /upload_file endpoint.
    """
    file = {"file": (filename, csv_content, "text/csv")}

    response = await async_test_client.post("/upload_file", files=file)
    assert response.status_code == 201

    # check the file exist
    store = create_store()
    try:
        meta = await obstore.head_async(store, filename)
        file_exists = True
    except FileNotFoundError:
        file_exists = False

    assert file_exists
    assert meta["size"] == len(csv_content)

    # Query DB for metadata
    stmt = select(models.File).where(models.File.filename==filename)
    file_metadata = (await get_test_db_session.execute(stmt)).scalars().first()

    assert file_metadata is not None
    assert file_metadata.filename == filename
    assert meta["size"] == file_metadata.size

    csv_content_txt = csv_content.decode("utf-8")
    num_cols = len(csv_content_txt.split('\n')[0].split(','))
    num_rows = len(csv_content_txt.split('\n'))-1

    assert num_cols == file_metadata.num_cols
    assert num_rows == file_metadata.num_rows


