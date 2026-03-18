import pytest
import pytest_asyncio

from app import models
from datetime import datetime
import json


@pytest.mark.parametrize(
        "filename,size,num_rows,num_cols,created_at",
    [
        ("file1.csv",4200,5,3,datetime.now()),
        ("file2.csv",10000,10,6,datetime.now()),
        ("file3.csv",5000,20,9,datetime.now()),
    ]
)
@pytest.mark.asyncio
async def test_get_files(async_test_client,get_test_db_session,filename,size,num_rows,num_cols,created_at):
    """Test GET /files endpoint using manual file metadata entries in the DB."""
    file= models.File(filename=filename,size=size,num_rows=num_rows,num_cols=num_cols,created_at=created_at)

    get_test_db_session.add(file)
    await get_test_db_session.commit()
    response = await async_test_client.get('/files')

    assert response.status_code == 200
    data = response.json()

    # assert filenames exist
    filenames = [f["filename"] for f in data['items']]
    assert filename in filenames



@pytest_asyncio.fixture
async def uploaded_csvs(async_test_client):
    """Upload csv files to be used for the integeration test."""
    csv_files = [
        ("file1.csv", b"gene_id,gene_name\n1,BRCA1\n2,TP53"),
        ("file2.csv", b"gene_id,gene_name\n3,EGFR\n4,ALK"),
        ("file3.csv", b"gene_id;gene_name\n5;KRAS\n6;NRAS"),  
    ]

    results = []
    for filename, content in csv_files:
        response = await async_test_client.post(
            "/upload_file",
            files={"file": (filename, content)}
        )
        assert response.status_code == 201
        results.append(response.json())

    return results 


@pytest.mark.asyncio
async def test_uploaded_filed_exist(async_test_client, uploaded_csvs):
    """Test GET /files after uploading files using the 'uploaded_csvs' fixture."""    

    response = await async_test_client.get("/files")
    assert response.status_code == 200
    files_response= response.json()

    files_uploades = uploaded_csvs
    for f1,f2 in zip(files_response['items'],files_uploades):
        assert f1['filename'] == f2['filename']
        assert f1['size'] == f2['size']
        assert f1['num_rows'] == f2['num_rows']
        assert f1['num_cols'] == f2['num_cols']
        assert f1['created_at'] == f2['created_at']



@pytest.mark.asyncio
async def test_get_file_metadata_by_id(async_test_client,uploaded_csvs):
    """Test GET /files/{id}/metadata endpoint to get metadata of a file given its ID."""    
    file_id =2
    response = await async_test_client.get(f'/files/{file_id}/metadata')
    assert response.status_code == 200
    file = response.json()

    # assert filemetadata fields
    assert uploaded_csvs[file_id-1]['filename'] == file["filename"]
    assert uploaded_csvs[file_id-1]['size'] == file["size"]
    assert uploaded_csvs[file_id-1]['num_rows'] == file["num_rows"]
    assert uploaded_csvs[file_id-1]['num_cols'] == file["num_cols"]
    assert uploaded_csvs[file_id-1]['created_at'] == file["created_at"]




@pytest.mark.asyncio
async def test_get_file_content_stream(async_test_client, uploaded_csvs):
    """Test retrieving file content via GET /files/{id}/data endpoint."""     
    file_id = 1

    response = await async_test_client.get(f"/files/{file_id}/data")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-ndjson"
    assert "attachment" in response.headers["content-disposition"]

    # get the streamed NDJSON lines
    lines = []
    async for chunk in response.aiter_text():
        lines.extend(chunk.splitlines())

    # parse each line
    records = [json.loads(line) for line in lines]

    assert records == [
        {"gene_id": "1", "gene_name": "BRCA1"},
        {"gene_id": "2", "gene_name": "TP53"},
    ]



@pytest.mark.asyncio
async def test_files_pagination(async_test_client,uploaded_csvs):
    """Test pagination with GET /files."""
    response = await async_test_client.get("/files?limit=2&offset=0")
    data = response.json()

    assert response.status_code == 200
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0
