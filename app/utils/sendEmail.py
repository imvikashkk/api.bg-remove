import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException
from app.core.config import SMTP_EMAIL, SMTP_EMAIL_PASS

def send_email(subject: str, body: str, to_email: str):
    try:
        from_email = SMTP_EMAIL
        password = SMTP_EMAIL_PASS

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")
    
def sendVerificationOTP(name:str, otp:str, to_email: str) :
        html_template = """
            <html>
  <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333;">
    <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
      <h2 style="color: #2d2d2d;">OTP Verification Code</h2>
      <p style="font-size: 16px; color: #555;">Hi <strong>{name}</strong>,</p>
      <p style="font-size: 16px; color: #555;">
        Thank you for signing up with us. Please use the following One-Time Password (OTP) to verify your email address:
      </p>
      
      <div style="padding: 10px; background-color: #f0f0f0; font-size: 24px; color: #333; text-align: center; border-radius: 4px; margin: 20px 0;">
        <strong>{otp}</strong>
      </div>

      <p style="font-size: 16px; color: #555;">
        If you did not request this OTP, please ignore this email or contact support.
      </p>
      <p style="font-size: 16px; color: #555;">OTP expires in 10 minutes.</p>
      
      <p style="font-size: 16px; color: #555;">Thank you for using our service!</p>
      
      <p style="font-size: 14px; color: #888;">If you have any questions, feel free to reach out to us.</p>
    </div>
  </body>
</html>
"""
        html_content = html_template.format(name=name, otp=otp)
        subject = "Your OTP Verification Code | BG-AI REMOVE"
        send_email(subject, html_content, to_email)

def sendForgotPassOTP(name:str, otp:str, to_email: str) :
        html_template = """
            <html>
  <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333;">
    <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
      <h2 style="color: #2d2d2d;">Forgot Password | OTP Verification Code</h2>
      <p style="font-size: 16px; color: #555;">Hi <strong>{name}</strong>,</p>
      <p style="font-size: 16px; color: #555;">
        Thank you for signing up with us. Please use the following One-Time Password (OTP) to verify your email address:
      </p>
      
      <div style="padding: 10px; background-color: #f0f0f0; font-size: 24px; color: #333; text-align: center; border-radius: 4px; margin: 20px 0;">
        <strong>{otp}</strong>
      </div>

      <p style="font-size: 16px; color: #555;">
        If you did not request this OTP, please ignore this email or contact support.
      </p>
      <p style="font-size: 16px; color: #555;">OTP expires in 10 minutes.</p>
      
      <p style="font-size: 16px; color: #555;">Thank you for using our service!</p>
      
      <p style="font-size: 14px; color: #888;">If you have any questions, feel free to reach out to us.</p>
    </div>
  </body>
</html>
"""
        html_content = html_template.format(name=name, otp=otp)
        subject = "Forgot Password | Your OTP Verification Code | BG-AI REMOVE"
        send_email(subject, html_content, to_email)