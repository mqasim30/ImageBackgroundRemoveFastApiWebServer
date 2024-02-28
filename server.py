import logging
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool
from rembg import remove
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Background Remover API is running"}
    
async def remove_background_async(image_data):
    logger.info("Starting background removal")
    result_image = await run_in_threadpool(remove, image_data)
    logger.info("Background removal completed")
    return result_image

@app.post("/remove-bg/")
async def remove_bg(file: UploadFile = File(...)):
    logger.info(f"Received image upload: {file.filename}")
    input_image = Image.open(io.BytesIO(await file.read()))
    logger.info("Image opened successfully")
    output_image = await remove_background_async(input_image)
    
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    logger.info("Processed image and returning to client")
    
    return StreamingResponse(io.BytesIO(img_byte_arr.getvalue()), media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
