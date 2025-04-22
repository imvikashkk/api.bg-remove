from fastapi import APIRouter, Request, Response, status, Depends
from fastapi.responses import JSONResponse
from app.controllers import user_controller
from app.core.config import PRODUCTION
from app.schemas.user_schema import SubscriberCreate, UserCreate, LoginSchema, Email_OTP_Request, Email_Verify_Request, ForgotPassSetPass_Req
from app.utils.jwt_verification import verify_token

router = APIRouter()

@router.post("/register")
async def register_user(user: UserCreate):
    return await user_controller.register_user(user)

@router.post("/login")
async def login_user(data: LoginSchema):
    return await user_controller.login_user(data)

@router.post("/logout")
async def logout(request: Request):
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Successfully logged out"}
    )

    # Clear all cookies
    for cookie_name in request.cookies.keys():
        response.set_cookie(
            key=cookie_name,
            value="",
            httponly=True,
            secure=PRODUCTION,
            samesite="lax",
            max_age=0,
            expires=0,
            path="/"
        )

    return response



@router.post("/check_session")
def check_session(request: Request, user=Depends(verify_token)):
    return  user_controller.user_session(request)


@router.post("/send_otp_verification")
async def sendOTP_user(data: Email_OTP_Request):
    return await user_controller.verify_user_otp_send(data)

@router.post("/email_verification")
async def email_verify_user(data: Email_Verify_Request):
    return await user_controller.verify_user_email(data)

@router.post("/forgot_pass/send_otp")
async def send_otp_forgot_pass(data: Email_OTP_Request):
    return await user_controller.forgot_pass_otp_send(data)

@router.post("/forgot_pass/update_password")
async def set_pass_forgot_pass(data: ForgotPassSetPass_Req):
    return await user_controller.forgot_password_set_password(data)


@router.post("/subscribe")
async def subscribe_future_updtes(data: SubscriberCreate):
    return await user_controller.subscribe(data)
