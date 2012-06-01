import win32com, win32com.client, pythoncom
import win32security
from common.logger import log

def GetADObject(principal):
	try:
		log.Info('Get AD Object: ' + principal)
		sid, domain, type = win32security.LookupAccountName('', principal)
		log.Info(str(sid))
		user = win32com.client.GetObject("LDAP://%s/<SID=%s>" % (domain, str(sid)[6:]))
		return user, str(sid)[6:]
	except BaseException, e:
		log.Debug("GetADObject; Unable to resolve display name. Error: %s"%str(e))
		return None, None

