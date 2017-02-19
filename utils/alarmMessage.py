import smtplib
from email.header import Header
from email.mime.text import MIMEText

g_smtp_host='smtp.exmail.qq.com'
g_smtp_port = 25
g_sender = 'keyongxing@hallowsec.com'
g_password = 'keyxP@33'
#g_receivers = ['1191182126@qq.com']

def send_alarm_mail(receivers, subject, content):
	message = MIMEText(content, 'plain', 'utf-8')
	message['From'] = '<%s>' %g_sender
	message['To'] = str(receivers)
	message['Subject'] = Header(subject, 'utf-8')
	
	smtp_obj = smtplib.SMTP()
	smtp_obj.connect(g_smtp_host, g_smtp_port)
	smtp_obj.login(g_sender, g_password)
	smtp_obj.sendmail(g_sender, receivers, message.as_string())
	smtp_obj.quit()