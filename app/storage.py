import os
import csv
import orjson
import codecs
from typing import Dict
from fastapi import UploadFile, File
from obstore.store import LocalStore, S3Store, GCSStore,from_url
from obstore import put_async, get_async
from io import StringIO
from pathlib import Path

from .config import settings



    
STORE_CACHE = {}



def get_store(store_type: str):
    """
    Return an instance of the appropriate Obstore based on the provided type.
    The instance is cached in STORE_CACHE for use throughout the app.
    """
    if store_type in STORE_CACHE:
        return STORE_CACHE[store_type]

    # if store_type == "local":
    #     UPLOAD_DIR = settings.upload_root / settings.upload_dir
    #     os.makedirs(UPLOAD_DIR, exist_ok=True)
    #     store = LocalStore(UPLOAD_DIR)
    # elif store_type == "s3":
    #     store = S3Store(bucket_name="my_bucket")
    # elif store_type == "gcs":
    #     store = GCSStore(bucket_name="my_bucket")
    # else:
    #     raise ValueError(f"Unknown store type: {store_type}")


    if store_type == "file":
        UPLOAD_DIR = settings.upload_root / settings.upload_dir
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    store = from_url(f"{settings.default_store_type}:///{Path.home()}/{settings.upload_dir}")

    STORE_CACHE[store_type] = store
    return store




async def store_file(file:UploadFile=File(...),store_type:str="")-> Dict:
    """
    Store the given file in the specified Obstore type. Extract and return the file metadata.
    """
 
    store = get_store(store_type)
    filename = file.filename
    size = file.size
   
    # Split the file content into chunks
    async def upload_file_in_chunks(file: UploadFile, chunk_size: int = 5 * 1024 * 1024):
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            yield chunk
    async_stream =  upload_file_in_chunks(file)


    # Store file using obstore
    put_result: "obstore.PutResult" = await put_async(
        store,
        filename,
        async_stream,
        chunk_size=5 * 1024 * 1024,
    )

    # Collect the number of rows and columns from the chunks
    reader = await get_async(store, filename)
    num_rows = 0
    num_cols = 0
    first_line_done = False
    buffer = ""
    delimiter = ""
    sniffer = csv.Sniffer() #To accept different delimiters, e.g., ; and ,


    async for chunk in reader.stream(min_chunk_size=5*1024*1024):
        buffer += chunk.decode("utf-8")
        lines = buffer.split("\n")
        buffer = lines.pop()
        for line in lines:
            if not first_line_done:
                delimiter = sniffer.sniff(lines[0]).delimiter
                num_cols = len(next(csv.reader(StringIO(line), delimiter=delimiter))) 
                first_line_done = True
            num_rows += 1

    if buffer.strip():
        num_rows += 1
 
    file_metadata = {
        "filename": filename,
        "size": size,  
        "num_rows": num_rows-1,
        "num_cols": num_cols
    }   
    return file_metadata
    



async def stream_csv_as_json(filename:str,store_type:str):
    """
    Read a CSV file from the given Obstore type and stream its contents in chunked JSON format.   
    """
    store = get_store(store_type)
    result = await store.get_async(filename)
    stream = result.stream(min_chunk_size=5 * 1024 * 1024)

    # Create an instance to safely decode UTF-8 from streamed chunks.
    decoder = codecs.getincrementaldecoder("utf-8")()
    buffer = ""
    header = None
    delimiter = ""
    sniffer = csv.Sniffer() # To accept different delimiters, e.g., ; and ,
    async for chunk in stream:
        # Decode each chunk 
        buffer += decoder.decode(chunk)
        # Split into lines
        lines = buffer.split("\n")
        buffer = lines.pop()  # keep last partial line

        for line in lines:
            if not line.strip():
                continue

            if header is None:
                delimiter = sniffer.sniff(lines[0]).delimiter
                header = next(csv.reader(StringIO(line), delimiter=delimiter))
                continue

            values = next(csv.reader(StringIO(line), delimiter=delimiter))
            row = dict(zip(header, values))

            # Yield one json object per row
            yield orjson.dumps(row) + b"\n"

     # Include the last line if exists.
    if buffer.strip() and header:
        values = next(csv.reader(StringIO(buffer), delimiter=delimiter))
        row = dict(zip(header, values))
        yield orjson.dumps(row) + b"\n"