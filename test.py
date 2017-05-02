import smtplib


msg = ""

server = smtplib.SMTP('smtp.gmail.com',587)
server.ehlo()
server.starttls()
server.ehlo()
server.login('verdusatest@gmail.com','happycrayon')
server.sendmail('verdusatest@gmail.com','tomkoch96@yahoo.com',msg)
server.close()
