"""
MSI_to_BES.py

This script takes a folder of MSI installers and generates BigFix Tasks to Install and Uninstall

Written by James Stewart   -   james@jgstew.com
Started 2014

"""

# pylint: skip-file
# pylint: disable-all
# prevent *.pyc creation:   http://stackoverflow.com/questions/154443/how-to-avoid-pyc-files
# import sys
# sys.dont_write_bytecode = True

from BES_CONFIG import *
""" Example:
BES_ROOT_SERVER_DNS  = "BESroot.DOMAIN.TLD"
BES_ROOT_SERVER_PORT = "52311"
BES_USER_NAME = "BES_USER_NAME"
BES_PASSWORD = "BES_PASSWORD"
BES_CUSTOM_SITE = "JamesTesting"
BES_DEBUGGING = "testing"
BES_INSTALLERS_LOCATION = "C:\temp"
"""


#from msilib import *
def GetMsiProperty(path ,property):
    # requires "from msilib import *"
    db = OpenDatabase(path, MSIDBOPEN_READONLY)
    view = db.OpenView ("SELECT Value FROM Property WHERE Property='" + property + "'")
    view.Execute(None)
    result = view.Fetch()
    #print dir(result)
    return result.GetString(1)


def BesRootUrl():
    return BES_ROOT_SERVER_DNS + ":" + BES_ROOT_SERVER_PORT


def BesRootUploadsUrl(protocol="http://"):
    return protocol + BesRootUrl() + "/Uploads/"


def BesRootApiUploadUrl():
    return "https://" + BesRootUrl() + "/api/upload"


def GetMsiFilePathsFromFolder(path):
    import os
    filepaths = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if (file.endswith(".msi") or file.endswith(".MSI")):
                filepaths.append(os.path.join(root, file))
    return filepaths


def GetNameVersionFromMsi(path):
    version = GetMsiProperty(path, "ProductVersion")
    name = GetMsiProperty(path, "ProductName")
    return (path,name,version)


def GetInfoMultipleMsis(paths):
    msiinfo=[]
    for path in paths:
        msiinfo.append(BesCreateTask(path))
    return msiinfo


def GetInstallTitleFromMSI(path):
    return GetTitleFromMSI(path)


def GetTitleFromMSI(path, task_type = "Install"):
    return task_type + '- %s v%s' % (GetMsiProperty(path, "ProductName"),GetMsiProperty(path, "ProductVersion"))


def GetInstallRelevanceFromMSI(path):
    return ('not exists keys whose (value "DisplayName" of it as string starts with "%s" AND (value "DisplayVersion" of it as string as version) >= "%s" as version) of keys "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" of (registry;native registry)' % (GetMsiProperty(path, "ProductName"),GetMsiProperty(path, "ProductVersion")))


def GetFileNameFromPath(path):
    # http://stackoverflow.com/questions/8384737/python-extract-file-name-from-path-no-matter-what-the-os-path-format
    import ntpath
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def GetActionScriptMSI(file_path, task_type = "Install"):
    if (task_type == "Uninstall"):
        return GetComments(file_path, task_type) + GetUninstallActionScriptMSI(file_path) + "\n"
    else:
        return GetComments(file_path, task_type) + GetInstallActionScriptMSI(file_path) + "\n"

def GetRelevanceMSI(file_path, task_type = "Install"):
    if (task_type == "Uninstall"):
        return GetUninstallRelevanceMSI(file_path)
    else:
        return GetInstallRelevanceFromMSI(file_path)


def GetComments(file_path, task_type = "Install"):
    return "\n// %s \n// Number of files in same directory: %s\n" % ( file_path, CountNumFilesInDir(file_path) )


def GetSysTracerActionScript(snapshot_name):
    if BES_DEBUGGING:
        runsystracer = ''
        runsystracer += 'if {exists file "C:\Program Files\SysTracer\SysTracer.exe"}\n'
        runsystracer += '   waithidden "C:\Program Files\SysTracer\SysTracer.exe" -quiet -scan rfa -name "' + snapshot_name + '"\n'
        runsystracer += 'endif\n\n'
        return runsystracer
    else:
        return ""


def GetInstallActionScriptMSI(path):
    preinstall = GetSysTracerActionScript("PreInstall-"+GetMsiProperty(path, "ProductName"))
    postinstall = GetSysTracerActionScript("PostInstall-"+GetMsiProperty(path, "ProductName"))
    return GetPrefetchSingleFile(path) + '\n\n' + preinstall + 'wait msiexec /i "{(pathname of file "%s" of folder "__Download" of client folder of current site)}" /qn /norestart DESKTOP_SHORTCUTS=0 ALLUSERS=1\n\n%s' % (GetFileNameFromPath(path), postinstall)


def GetUninstallActionScriptMSI(path):
    return 'wait msiexec /x "{unique value of names of keys whose (value "DisplayName" of it as string starts with "%s" AND value "UninstallString" of it as string as lowercase contains "msiexec") of keys "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" of (registry;native registry)}" /qn /norestart' % GetMsiProperty(path, "ProductName")


def GetUninstallRelevanceMSI(path):
    return 'exists keys whose (value "DisplayName" of it as string starts with "%s" AND value "UninstallString" of it as string as lowercase contains "msiexec") of keys "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" of (registry;native registry)' % GetMsiProperty(path, "ProductName")


def GetPrefetchSingleFile(path, url = "", file_name = ""):
    import os
    import hashlib
    import urllib

    if not file_name:
      file_name = GetFileNameFromPath(path)

    if not url:
      url = BesRootUploadsUrl() + GetSHA1(path) + "/" + file_name

    #  http://stackoverflow.com/questions/961632/converting-integer-to-string-in-python
    return "prefetch %s sha1:%s size:%s %s" % (file_name, GetSHA1(path) , os.path.getsize(path), urllib.quote(url, ":/"))


def CountNumFilesInDir(path, file_type = "*"):
    # http://stackoverflow.com/questions/3883138/how-do-i-read-the-number-of-files-in-a-folder-using-python
    import os
    if os.path.isfile(path):
        path = os.path.dirname(path)
    # Counts the number of files in a directory - does a check to only count files and not directories within the directory
    return sum(os.path.isfile(os.path.join(path, f)) for f in os.listdir(path))


def ListFilesInDir(path):
    import os
    if os.path.isfile(path):
        path = os.path.dirname(path)
    return "TODO_WorkInProgress"


def BesImportBesFile(file_path):
    import os
    import urllib2
    import base64
    from xml.dom import minidom

    if os.path.isfile(file_path):
        besData = open(file_path).read()  # read xml from file
        # Create Request
        request = urllib2.Request("https://" + BesRootUrl() + "/api/tasks/custom/" + BES_CUSTOM_SITE)
        # Add Console Auth
        authString = base64.encodestring('%s:%s' % (BES_USER_NAME, BES_PASSWORD)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % authString)
        request.add_header("Content-Type", "application/xml")
        request.add_data(besData)

    try:
        return urllib2.urlopen(request)
    except (urllib2.HTTPError,error):
        print ("HTTPError: [%s] %s" % (error.code, error.read()))
        sys.exit(1)
#    except urllib2.URLError, error:
#        print ("URLError: %s" % (error.args))
#        sys.exit(1)


def BesUploadFile(file_path):
    # currently Requires Master Operator account
    # https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/Tivoli%20Endpoint%20Manager/page/RESTAPI%20Upload
    import os
    import urllib2, urllib
    import base64
    from xml.dom import minidom

    url = "https://" + BesRootUrl() + "/api/upload"
    if os.path.isfile(file_path):
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, BES_USER_NAME, BES_PASSWORD)
        auth = urllib2.HTTPBasicAuthHandler(password_manager) # create an authentication handler

        opener = urllib2.build_opener(auth) # create an opener with the authentication handler
        urllib2.install_opener(opener) # install the opener...

        request = urllib2.Request(url) # Manual encoding required
        request.add_header("Content-Disposition", 'attachment; filename="%s"' % GetFileNameFromPath(file_path))
        # Read bes_file data and add to request
        postData = open(file_path, "rb").read()

        request.add_data(postData)

        handler = urllib2.urlopen(request)

        return handler.read()
    else:
        return ""

def newNode(doc, elementName, nodeText = None, elementAttributes = {}):
    import xml.dom.minidom
    doc = xml.dom.minidom.Document()
    newElement = xml.dom.minidom.Document().createElement(elementName)

    if nodeText:
        if any((character in """<>&'\"""") for character in nodeText):
                newElement.appendChild(xml.dom.minidom.Document().createCDATASection(nodeText))
        else:
                newElement.appendChild(xml.dom.minidom.Document().createTextNode(nodeText))

    if elementAttributes:
        for attribute in elementAttributes:
                newElement.setAttribute(attribute, elementAttributes[attribute])

    return newElement

def newMIME(doc, mimeName, mimeValue):
    import xml.dom.minidom
    doc = xml.dom.minidom.Document()
    newMIMEElement = xml.dom.minidom.Document().createElement('MIMEField')

    newMIMEElement.appendChild(newNode(xml.dom.minidom.Document(), 'Name', mimeName))
    newMIMEElement.appendChild(newNode(xml.dom.minidom.Document(), 'Value', mimeValue))

    return newMIMEElement

def BesSuccessCriteria(SuccessCriteria = 'OriginalRelevance'):
    return newNode(xml.dom.minidom.Document(), 'SuccessCriteria', None, {'Option': SuccessCriteria} )

def newlinkDescription(fullDescription):
    import xml.dom.minidom

    newDescriptionElement = xml.dom.minidom.Document().createElement('Description')

    newDescriptionElement.appendChild(newNode(xml.dom.minidom.Document(), 'PreLink', fullDescription[0]))
    newDescriptionElement.appendChild(newNode(xml.dom.minidom.Document(), 'Link', fullDescription[1]))
    newDescriptionElement.appendChild(newNode(xml.dom.minidom.Document(), 'PostLink', fullDescription[2]))

    return newDescriptionElement


def newAction(actionDict):
    import xml.dom.minidom
    actionDict['Description'] = ['%s - Click ' % actionDict['ActionNumber'], 'here', ' to take action.']

    newAction = newNode(xml.dom.minidom.Document(), actionDict['ActionName'], None, {'ID': actionDict['ActionNumber']})
    newAction.appendChild(newlinkDescription(actionDict['Description']))
    newAction.appendChild(newNode(xml.dom.minidom.Document(), 'ActionScript', actionDict['ActionScript'], {'MIMEType': 'application/x-Fixlet-Windows-Shell'}))
    newAction.appendChild(newNode(xml.dom.minidom.Document(), 'SuccessCriteria', None, {'Option': actionDict['SuccessCriteria']}))

    return newAction

def BesCreateTask(file_path, task_type = "Install"):
    import os
    import datetime
    import hashlib
    from collections import OrderedDict
    import xml.dom.minidom
    from time import gmtime, strftime

    details = OrderedDict(( ('Category' 	    , "Software Distribution" ),
			    ('DownloadSize'	    , str(os.path.getsize(file_path)) ),
			    ('Source'		    , "MSI_to_BES" ),
			    ('SourceID'		    , 'jgstew' ),
			    ('SourceReleaseDate'    , str(datetime.datetime.now())[:10]),
			    ('SourceSeverity'	    , ""),
			    ('CVENames'		    , ""),
			    ('SANSID' 		    , ""),
                            ))

    doc = xml.dom.minidom.Document()
    root = newNode(doc, 'BES', None, {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsi:noNamespaceSchemaLocation': 'BES.xsd'})
    doc.appendChild(root)
    message = newNode(doc, 'Task')
    root.appendChild(message)

    # Append Title and Description
    message.appendChild(newNode(doc, 'Title', GetTitleFromMSI(file_path,task_type)))
    message.appendChild(newNode(doc, 'Description', GetTitleFromMSI(file_path,task_type)))

    # Append Relevance

    message.appendChild(newNode(doc, 'Relevance', '/* Windows Only */ windows of operating system'))
    message.appendChild(newNode(doc, 'Relevance', '/* WinXP or later */ version of operating system >= "5.1"'))
    message.appendChild(newNode(doc, 'Relevance', GetRelevanceMSI(file_path, task_type) ))

    # Append Details Dictionary
    for key, value in details.items():
        message.appendChild(newNode(doc, key, value))

    # Append MIME Source Data
    message.appendChild(newMIME(doc, 'x-fixlet-source', os.path.basename(__file__)))
    message.appendChild(newMIME(doc, 'x-fixlet-modification-time', strftime("%a, %d %b %Y %X +0000", gmtime())))

    message.appendChild(newNode(doc, 'Domain', 'BESC'))

    # Append Default Action
    action  = OrderedDict(( ('ActionName' 	    , "DefaultAction" ),
			    ('ActionNumber'	    , "Action1" ),
			    ('Description'	    , None ),
			    ('ActionScript'	    , GetActionScriptMSI(file_path, task_type) ),
			    ('SuccessCriteria'      , 'OriginalRelevance' ),
                            ))
    message.appendChild(newAction(action))
    return doc.toxml(encoding="UTF-8")
    #return doc.toprettyxml(indent="    ", newl="\r\n", encoding="utf-8")

def writeFile(file_path, content):
    out_file_handle = open( file_path ,"wb")
    out_file_handle.write( content )
    return out_file_handle.name

def ProcessMultipleMSIs(path):
    file_paths_msi = GetMsiFilePathsFromFolder(path)
    file_paths_msi_filtered = []
    print(file_paths_msi)
    #numfiles = []

    for file_path in file_paths_msi:
        if 1 == CountNumFilesInDir(file_path):
            file_paths_msi_filtered.append(file_path)
            print(BesImportBesFile(writeFile(file_path + "-Install.bes", BesCreateTask(file_path, "Install"))))
            print(BesImportBesFile(writeFile(file_path + "-Uninstall.bes", BesCreateTask(file_path, "Uninstall"))))
            print(BesUploadFile(file_path))

    return file_paths_msi_filtered

# NOTE: there is a more efficient way to get the output of 2 hashes for the same file at once
def GetSHA1(file_path):
    import os
    import hashlib
    return str( hashlib.sha1( open(file_path, "rb").read() ).hexdigest() )

def GetSHA256(file_path):
    import os
    import hashlib
    return str( hashlib.sha256( open(file_path, "rb").read() ).hexdigest() )


if __name__ == "__main__":
    print(BES_INSTALLERS_LOCATION)
    print(CountNumFilesInDir(BES_INSTALLERS_LOCATION))
    print(GetMsiFilePathsFromFolder(BES_INSTALLERS_LOCATION))
    #print str( GetSHA1("P:\Packagers\James\ITDSDP\Sybase\Sybase.MSI") )
    #print GetInstallActionScriptMSI("C:\Users\jgstew\Downloads\INSSIDER\inSSIDer-installer-3.0.7.48.msi")
    print(ProcessMultipleMSIs(BES_INSTALLERS_LOCATION))
    #print BesUploadFile("P:\Packagers\James\CoseSDP\Majiq\MajiqWindowsShortcut.msi")
    #print GetInfoMultipleMsis(GetMsiFilePathsFromFolder("C:\Users\jgstew\Downloads"))
    #print BesCreateTask("C:\Users\jgstew\Downloads\inSSIDer-installer-3.0.7.48.msi")
