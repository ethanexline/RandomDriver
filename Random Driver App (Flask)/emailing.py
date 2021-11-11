# libraries to be imported 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
import time

class emailing:
    
    def __init__(self, to_address, subject, body, filename = False, filename_path = False):
        self.fromaddr = "Postmaster <{REDACTED}>"
        self.toaddr = to_address
        self.subject = subject
        self.body = body
        self.filename = filename
        self.filename_path = filename_path
    
    def send_it(self, msg):

        try:
            # creates SMTP session 
            s = smtplib.SMTP('outbound-us1.ppe-hosted.com', 25) 
            
            # start TLS for security 
            s.starttls() 
                
            # Converts the Multipart msg into a string 
            text = msg.as_string() 
            
            # sending the mail 
            s.sendmail(self.fromaddr, self.toaddr, text) 
            
            # terminating the session 
            s.quit()
        except Exception as e:
            time.sleep(30)
            self.send_it(msg)


    def send_mail(self):
        # instance of MIMEMultipart 
        msg = MIMEMultipart() 
          
        # storing the senders email address   
        msg['From'] = self.fromaddr 
          
        # storing the receivers email address  
        msg['To'] = self.toaddr 
          
        # storing the subject  
        msg['Subject'] = self.subject
          
        # string to store the body of the mail 
        body = self.body

          # attach the body with the msg instance 
        msg.attach(MIMEText(body, 'html')) 
        if self.filename:
            
            for file_ in self.filename:
                # open the file to be sent  
                filename = file_
                attachment = open(self.filename_path + file_ , "rb") 
                
                # instance of MIMEBase and named as p 
                p = MIMEBase('application', 'octet-stream') 
                
                # To change the payload into encoded form 
                p.set_payload((attachment).read()) 
                
                # encode into base64 
                encoders.encode_base64(p) 
                
                p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
                
                # attach the instance 'p' to instance 'msg' 
                msg.attach(p) 
          
        self.send_it(msg)





