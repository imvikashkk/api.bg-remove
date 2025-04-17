from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from app.schemas.user_schema import SubscriberCreate, UserCreate, LoginSchema,  Email_OTP_Request, Email_Verify_Request, ForgotPassSetPass_Req
from app.services.user_services import create_user, authenticate_user, verify_user_sendOTP, verify_user, forgot_password_sendOTP, forgot_password, subscribe_update

import logging
logger = logging.getLogger(__name__)


async def register_user(user: UserCreate):
    try:
        success, created_user = await create_user(user.model_dump())  # FIX: convert model to dict
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "message": created_user}
            )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": "User registered successfully",
                "data": created_user.model_dump()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": "Something went wrong. Please try again."}
        )


async def verify_user_otp_send(data:Email_OTP_Request):
    try:
        success, response = await verify_user_sendOTP(data.model_dump())
        if not success:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"success":False, "message":response})
        return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"success": True, "message": "OTP has been sent successfully.", "data": response}
)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(status_code=500, detail={"success":False, "message":"Something went wrong. Please try again."})
    
async def subscribe(data:SubscriberCreate):
    try:
        success, response = await subscribe_update(data.model_dump())
        if not success:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"success":False, "message":response})
        return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"success": True, "message": "Subscribed Successfully!", "data": response}
)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during subscription: {e}")
        raise HTTPException(status_code=500, detail={"success":False, "message":"Something went wrong. Please try again."})
    

async def verify_user_email(data:Email_Verify_Request):
    try:
        success, response = await verify_user(data.model_dump())
        if not success:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"success":False, "message":response})
        return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"success": True, "message": "User Verified Successfully!", "data": response}
)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(status_code=500, detail={"success":False, "message":"Something went wrong. Please try again."})


async def forgot_pass_otp_send(data:Email_OTP_Request):
    try:
        success, response = await forgot_password_sendOTP(data.model_dump())
        if not success:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"success":False, "message":response})
        return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"success": True, "message": "OTP has been sent successfully.", "data": response}
)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(status_code=500, detail={"success":False, "message":"Something went wrong. Please try again."})
    

async def forgot_password_set_password(data:ForgotPassSetPass_Req):
    try:
        success, response = await forgot_password(data.model_dump())
        if not success:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"success":False, "message":response})
        return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"success": True, "message": "Password has been changed successfully.", "data": response}
)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(status_code=500, detail={"success":False, "message":"Something went wrong. Please try again."})


async def login_user(login_data: LoginSchema):
    try:
        success, response = await authenticate_user(login_data.model_dump())
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"success":False, "message":response})

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(status_code=500, detail={"success":False, "message":"Something went wrong. Please try again."})
    
def user_session(request:Request):
      user = getattr(request.state, "user", {"id":"", "email":"", "firstname":"", "lastname":""})
      response = JSONResponse(status_code=status.HTTP_200_OK, content={"success":True, "user": user})
      return response
