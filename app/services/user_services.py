from fastapi import  status, Request
from fastapi.responses import JSONResponse
from app.core.config import IS_PRODUCTION
from app.core.database import db
from app.schemas.user_schema import UserCreate, UserResponse, LoginSchema, LoginResponse
from passlib.hash import bcrypt
from bson import ObjectId
from app.utils.jwt import create_access_token
import random
from app.utils.sendEmail import sendVerificationOTP, sendForgotPassOTP
from datetime import datetime, timedelta,  timezone


async def create_user(user_data: dict):
    required_fields = ["firstname", "lastname", "email", "password", "confirmpassword"]
    missing = [field for field in required_fields if field not in user_data or user_data[field] is None]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    # Check password match manually
    if user_data.get("password") != user_data.get("confirmpassword"):
        return False, "Password and Confirm Password did not match!"

    # Check for existing user
    existing_user = await db.users.find_one({"email": user_data.get("email")})
    if existing_user:
        return False, "Email already exists!"

    # Hash password
    hashed_password = bcrypt.hash(user_data["password"])
    user_data["password"] = hashed_password

    # Generate OTP
    otp = str(random.randint(10000000, 99999999))
    user_data["otp"] = otp
    user_data["otp_type"] = "verify"

    # Let Pydantic handle setting timestamps and otp_expiry
    try:
        user = UserCreate(**user_data)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return False, str(e)

    # Insert into MongoDB
    result = await db.users.insert_one(user.model_dump())

    # Send OTP email
    sendVerificationOTP(user.firstname, user.otp, user.email)

    # Return response
    return True, UserResponse(
        id=str(result.inserted_id),
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email
    )


async def verify_user_sendOTP(data: dict):
    required_fields = ["email"]
    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    # Fetch the user from the database
    user = await db.users.find_one({"email": data.get("email")})
    if not user:
        return False, "User not found!"
    
    if user.get("verified") == True:
        return False, "Already Verified!"
    
    # Generate a new OTP
    otp = str(random.randint(10000000, 99999999))

    # Prepare data for the update operation
    update_data = {
        "otp": otp,
        "otp_type": "verify",
        "updated_at": datetime.now(timezone.utc)  # Manually setting updated_at
    }

    # Set OTP expiry automatically
    # Here you can update otp_expiry manually if OTP is set.
    update_data["otp_expiry"] = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Update user document in MongoDB
    await db.users.update_one(
        {"email": data.get("email")},
        {"$set": update_data}
    )

    # Send OTP email
    sendVerificationOTP(user.get("firstname"), otp, user.get("email"))

    return True, {"email": user.get("email")}


async def verify_user(data: dict):
    required_fields = ["email", "otp"]
    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    user = await db.users.find_one({"email": data.get("email")})
    if not user:
        return False, "User not found!"
    
    if user.get("verified") is True:
        return False, "Already Verified!"
    
    if user.get("otp_type") != "verify":
        return False, "Invalid OTP!"
    
    if user.get("otp") != data.get("otp"):
        return False, "Invalid OTP!"
    
     # Check OTP expiry
    otp_expiry = user.get("otp_expiry")
    if otp_expiry is None:
        return False, "OTP Expired!"  # OTP is not set or expired already
    
    current_time = datetime.now(timezone.utc)
    
    # Ensure otp_expiry is timezone-aware
    if otp_expiry.tzinfo is None:
        otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)

    # Compare expiry time with current time
    if otp_expiry < current_time:
        return False, "OTP Expired!"
    
    # Update user verification status
    await db.users.update_one(
        {"email": data.get("email")},
        {"$set": {
            "otp": None,
            "otp_type": None,
            "otp_expiry": None,
            "verified": True,
            "updated_at": datetime.now(timezone.utc) 
        }}
    )

    return True, {"email": user.get("email")}


async def forgot_password_sendOTP(data: dict):
    required_fields = ["email"]
    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    # Fetch the user from the database
    user = await db.users.find_one({"email": data.get("email")})
    if not user:
        return False, "User not found!"
    
    # Generate a new OTP
    otp = str(random.randint(10000000, 99999999))

    # Prepare data for the update operation
    update_data = {
        "otp": otp,
        "otp_type": "forgotPass",
        "updated_at": datetime.now(timezone.utc)  # Manually setting updated_at
    }

    # Set OTP expiry automatically
    # Here you can update otp_expiry manually if OTP is set.
    update_data["otp_expiry"] = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Update user document in MongoDB
    await db.users.update_one(
        {"email": data.get("email")},
        {"$set": update_data}
    )

    # Send OTP email
    sendForgotPassOTP(user.get("firstname"), otp, user.get("email"))

    return True, {"email": user.get("email")}


async def forgot_password(data: dict):
    required_fields = ["email", "otp", "password", "confirmpassword"]
    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    if data.get("password") != data.get("confirmpassword"):
        return False, "Password and Confirm Password did not match!"

    # Fetch the user from the database
    user = await db.users.find_one({"email": data.get("email")})
    if not user:
        return False, "User not found!"
    
    if user.get("otp_type") != "forgotPass":
        return False, "Invalid OTP!"
    
    if user.get("otp") != data.get("otp"):
        return False, "Invalid OTP!"
    
     # Check OTP expiry
    otp_expiry = user.get("otp_expiry")
    if otp_expiry is None:
        return False, "OTP Expired!"  # OTP is not set or expired already
    
    current_time = datetime.now(timezone.utc)
    
    # Ensure otp_expiry is timezone-aware
    if otp_expiry.tzinfo is None:
        otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)

    # Compare expiry time with current time
    if otp_expiry < current_time:
        return False, "OTP Expired!"

    hashed_password = bcrypt.hash(data.get("password"))
    
    # Prepare data for the update operation
    update_data = {
        "otp": None,
        "otp_type": None,
        "otp_expiry" : None,
        "verified":True,
        "password" : hashed_password,
        "updated_at": datetime.now(timezone.utc)  
    }

    # Update user document in MongoDB
    await db.users.update_one(
        {"email": data.get("email")},
        {"$set": update_data}
    )

    return True, {"email": user.get("email")}


async def authenticate_user(data: dict):
    required_fields = ["email", "password", "remember_me"]
    missing = [field for field in required_fields if field not in data or data[field] is None]

    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    user = await db.users.find_one({"email": data.get("email")})
    if not user:
        return False, "User not found"

    if not bcrypt.verify(data.get("password"), user.get("password")):
        return False, "Invalid credentials!"
    
    if user.get("verified") != True :
        return False, "User not verified!"

    token, expiry = create_access_token(
        {"id": str(user["_id"]), "email": user["email"], "firstname":user["firstname"], "lastname":user["lastname"] },
        remember=data.get("remember_me")
    )

    login_response = LoginResponse(
        success = True,
        message = "User logged in successfully",
        data=UserResponse(
            firstname=user["firstname"],
            lastname=user["lastname"],
            email=user["email"],
            id=str(user["_id"])
        )
    )

    response = JSONResponse(status_code=status.HTTP_200_OK, content=login_response.model_dump())

     # Set the token in a secure, HttpOnly cookie
    max_age = int(timedelta(days=15).total_seconds()) if data.get("remember_me") else int(timedelta(hours=3).total_seconds())
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=IS_PRODUCTION,
        domain=".ai-bg-remover.com",
        samesite="lax",
        max_age=max_age,
        path="/"
    )


    return True, response


async def subscribe_update(user_data:dict):
    required_fields = ["email"]
    missing = [field for field in required_fields if field not in user_data or user_data[field] is None]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    alreadySubscribe = await db.subscribers.find_one({"email": user_data.get("email")})
    if alreadySubscribe and (user_data.get("force") is not True):
        return False, f"Already Subscribed!\n({user_data.get('email')})"
    if alreadySubscribe and (user_data.get("force") is True):
        await db.subscribers.update_one(
          {"email": user_data.get("email")},
          {"$set": {
            "updated_at": datetime.now(timezone.utc) 
          }}
        )
        return True, f"You are re-subscribed.\n({user_data.get('email')})"
    
    result = await db.subscribers.insert_one({
        "email":user_data.get("email"),
        "created_at":datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc) 
    })
    return True, f"You are subscribed.\n({user_data.get('email')})"
