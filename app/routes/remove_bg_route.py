from fastapi import APIRouter, UploadFile, File, Request, status
from fastapi.responses import JSONResponse
from app.controllers.remove_bg_controller import remove_bg_controller as remove_bg_logic
import base64

router = APIRouter()

@router.post("/remove_bg")
async def removebg_controller(
    request: Request,
    file: UploadFile = File(...)
):
    sd_img, sd_size, hd_img, hd_size = await remove_bg_logic(file)
    hd = getattr(request.state, "hd", False)
    additional = getattr(request.state, "jwt", {"success": False, "message": "Token not found!"})

    response_data = {
        "success": True,
        "message": "BG successfully removed",
        "additional": additional,
        "data": {
            "sd_image": base64.b64encode(sd_img).decode(),
            "sd_size": sd_size,
            "hd_size": hd_size
        }
    }

    if hd:
        response_data["data"]["hd_image"] = base64.b64encode(hd_img).decode()

    return JSONResponse(status_code=status.HTTP_200_OK, content=response_data)
