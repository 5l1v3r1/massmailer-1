#!/usr/bin/env python
#
########################
# Mass eMail script v1.0
#
#	Use this script to send a message via an SMTP relay
#	to a designated recipient list
#
#	~ Liviu Itoafa, Mitchell Hines 
#
#
# CHANGELOG
#
# v1.1
# ---- 
# * added semi-colon as a delimeter for TO_LIST in config (MH)
# * added support for HTML eMail message content which can be done in the msg.massmail file (MH)
#
########################################

import base64
import smtplib
import time
import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate

OK2 = '\033[93m'
OK = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'
VERBOSE = False
VERSION = 1.1

# ----------------- SEND EMAIL function ----------------------

def send_mail(server, from_address, from_name, to_address, subject, body_arg, return_addr, tls):

	msg = MIMEMultipart('alternative')
	msg['To'] = to_address
	msg['Date'] = formatdate(localtime = True)
	msg['Subject'] = subject
	msg.add_header('reply-to', return_addr)
	msg.add_header('from', from_name + "<" + from_address + ">")

	part1 = MIMEText(body_arg, 'plain')
	part2 = MIMEText(body_arg, 'html')

	msg.attach(part1)
	msg.attach(part2)

	try:
		smtp = smtplib.SMTP(server)
		smtp.set_debuglevel(VERBOSE)
		smtp.sendmail(from_address, to_address, msg.as_string())
		smtp.quit()
	except smtplib.SMTPException:
		print FAIL + "[-] Error: unable to send email to ", to_address, ENDC

# --------------------- PARSE includes/config.massmail -------------------

def parse_config(in_config):
	f = open(in_config, 'r')
	data = f.readlines()
	f.close()

	out_config = { "SMTP_SRV" : "", "TO_LIST" : [] , "FROM_NAME" : [] , "FROM_ADDR" : "" , "RET_ADDR" : "" , "SUBJECT" : "", "MSG_BODY" : "", "TIMEOUT" : "", "TLS" : 0 }

	for i in data:
		if not (i.startswith('#') or len(i) < 2):
			line = i.split("=")
			if line[0] == "SMTP_SRV":
				out_config['SMTP_SRV'] = line[1].strip()
			elif line[0] == "TO_LIST":
				out_config['TO_LIST'].append(line[1].strip())
			elif line[0] == "FROM_ADDR":
				out_config['FROM_ADDR'] = line[1].strip()
			elif line[0] == "FROM_NAME":
				out_config['FROM_NAME'] = line[1].strip().replace("\"", "")
			elif line[0] == "RET_ADDR":
				out_config['RET_ADDR'] = line[1].strip()
			elif line[0] == "SUBJECT":
				out_config['SUBJECT'] = line[1].strip()
			elif line[0] == "TIMEOUT":
				out_config['TIMEOUT'] = line[1].strip()
			elif line[0] == "TIMEOUT":
				out_config['TLS'] = line[1].strip()

	return out_config

#----------------- PARSE  includes/msg.massmail file to get email body ---------

def parse_body(name, message):

	try:
		fname = name.split(".")[0]
		fname = fname[0].upper() + fname[1:]
		f = open(message, "r")
		rd = f.read()
		rd=rd.replace("%FIRSTNAME%", fname)
		f.close()
	except IOError as e:
		print FAIL + "[-] Cannot open: %s" % (message)
		print "I/O error({0}): {1} - %s".format(e.errno, e.strerror) % (message)
		exit(1)
	except ValueError:
		print "Could not convert data to an integer."
	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise

	return rd

def banner():

	print base64.b64decode("IF9fICBfXyAgICAgICAgICAgICAgIF9fICBfXyAgICAgICBfIF8gICAgICAgICAgIAp8ICBcLyAgfCAgICAgICAgICAgICB8ICBcLyAgfCAgICAgKF8pIHwgICAgICAgICAgCnwgXCAgLyB8IF9fIF8gX19fIF9fX3wgXCAgLyB8IF9fIF8gX3wgfCBfX18gXyBfXyAKfCB8XC98IHwvIF9gIC8gX18vIF9ffCB8XC98IHwvIF9gIHwgfCB8LyBfIFwgJ19ffAp8IHwgIHwgfCAoX3wgXF9fIFxfXyBcIHwgIHwgfCAoX3wgfCB8IHwgIF9fLyB8ICAgCnxffCAgfF98XF9fLF98X19fL19fXy9ffCAgfF98XF9fLF98X3xffFxfX198X3wgIHYlcwotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLQoK")% str(VERSION),

if __name__ == "__main__":
	
	banner()
	if ( "-c" not in sys.argv or "-m" not in sys.argv):
		print "Usage: %s [options]" % (sys.argv[0])
		print "\nOptions:\n"
		print "\t-c\tconfig file"
		print "\t-m\tmessage file"
		print "\t-v\tverbose\n"
		print "Example: %s -c config.massmail -m msg.html -v" %(sys.argv[0])
		exit(1)

#----------- CONFIG prep -----------

	if ("-v" in sys.argv):
		VERBOSE = True
		print OK + "[+] Verbose mode enabled" + ENDC
	
	c_file = sys.argv[sys.argv.index("-c")+1]

	print OK2 + "[+] Parsing config file : %s ..." % (c_file)+ENDC
	config = parse_config(c_file)
	print OK2 + "[+] Parsing successful!"	+ENDC +"\n"
	
	server = config['SMTP_SRV']
	address_book = config['TO_LIST'][0].split(",").split(";")
	from_name = config['FROM_NAME']
	from_address = config['FROM_ADDR']
	ret_address = config['RET_ADDR']
	subject = config['SUBJECT']
	timeout = int(config['TIMEOUT'])
	tls = config['TLS']

#------------- EOF CONFIG ----------
#
# Now send emails
#-------------------------

	print OK + "[***] Entering email loop. Go grab a coffee..."+ENDC

	for addr in address_book:
		print "----------------------------------------------------"
		print OK + "[+] Sending Mail To " + addr, ENDC
		body = parse_body(addr, sys.argv[sys.argv.index("-m")+1])
		send_mail(server, from_address, from_name, addr, subject, body, ret_address, tls)
		time.sleep(timeout)
	print "-------------------------------------------------\n Finished sending %d emails.\n-------------------------------------------------" % len(address_book)

