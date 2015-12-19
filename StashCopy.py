import os
import re
from subprocess import Popen, PIPE

import sublime
import sublime_plugin


# Check known project names against reported repository name.
def getProject(repoName):
  projects = {
    'ADNET':  ['adconfigs','AdRouter','AdRouterBase','adserver','atg_stats','cachegenerator','Console','logsummarizer','marketplaceapi','marketplacelib','marketplaceui','sancdn.m','sanshared','sanslides','sanstack','tracker','tracker2s'],
    'ADBREP': ['alldbapi','alldbapiphpclient'],
    'ATTIC':  ['adserver1.0','cb.cbreports.webapp','cb.promotools.webapp','cb.sitebuilder.webapp','cb.sitewizard.webapp','DollaBillZ','labe.naiad.fms','labe.naiad.fms.asc','labe.naiad.fms.gateway','labe.naiad.fms.test','lbe.health','lbe.lgb','lbe.lib.XmlStreamsServer.js','lbe.lodef','lodef','ls.naiad.liveservices.gateway','ls.naiad.liveservices.libs','ls.naiad.liveservices.messagebus','ls.testrepo','lte.ffmpeg.test','lte.naiad.transcode.ffmpeg','lte.naiad.transcode.host','lte.naiad.transcode.queue','lvd.naiad.wowza','lvd.naiad.wowza.abr','lvd.naiad.wowza.auth','lvd.naiad.wowza.monitor','lvd.naiad.wowza.transcodecontrol','marketplaceapiold','marketplacedesign','marketplaceuiold','nc.balance','nc.helper','nc.ipv4','nc.platform','react.thinflash','san.flash.as3','sexadnet','sexadnet.generated.configs','sexadnet.qa','splunk','vm.n-liveservices-salt'],
    'BIL':    ['billing.prototype','fap.services','naiad.bling','naiad.descriptorsites'],
    'CB':     ['cambuilder.tools','cb.vm','naiad.cambuilder','naiad.cambuilder.webapp','naiad.sitebuilder'],
    'CM':     ['gorilla','gorilla-frontend'],
    'TV':     ['naiad.producer','tvbroadcast','xojo'],
    'DB':     ['db.bi','db.live'],
    'TOOLS':  ['atg-hubot','doggy','echelon','fci.make','jenkins-config','naiad.internal','networkshaper','senderella-scripts','splunk','staging','users','wallboard'],
    'ICF':    ['icf.core','icf.core.js','icf.example.app.php','icf.loms','icf.xment'],
    'INS':    ['auth.service','authorization.admin','authorization.api'],
    'MEMB':   ['icf.membership'],
    'MOB':    ['android.livecamapp','android.livecamapp.jenkinstest','android.livecamapp.release','android.livecamappcontrol','ios.bline'],
    'MH':     ['mh.admin','mh.core','mh.server'],
    'NC':     ['fci.ext','fci.perl','fci.php','fci.sauth','maxmind','merlin','naiad.core','naiad.exports','naiad.gfx','naiad.site','naiad.web'],
    'NODE':   ['atg-appconfig','atg-balance','atg-cluster-master','atg-fileconfig','atg-helper','atg-ipv4','atg-js-styleguide','atg-log','atg-platform','atg-s2-e2etest','atg-service-control','atg-service-wrapper','atg-transcode-process','atg-xmlstreamserver','libs'],
    'PROTO':  ['3dvision.silverlight','fuqt','googleglass','hworld','liveservices.translate','rad.modelservices.encoder','rad.webrtc','realman','streamatedesktop.tide'],
    'QA':     ['cambuilder.robot','membership.robot'],
    'SS':     ['atg.core.php','atg.lib.php','atg.service.phpdoc','naiad.lib.php','naiad.service.perfsearch','naiad.service.perfsearch.skin','svc.atg.example.nodejs','svc.atg.example.php'],
    'SM':     ['availperf.redis','naiad.css','naiad.skin','naiad.streamate','naiad.webapp.streamate','sdet.tools'],
    'SMM':    ['modelmedia','naiad.smm','performerdesktop.tide','TideSDK'],
    'SG':     ['dv.ffmpeg','dv.ffmpeg-wrapper','dv.transcode','dv.transcode.queue','enc.android','enc.atg-qt5','enc.control.service','enc.control.service.mobile.mock','enc.control.service.mock','enc.desktop','enc.ios','ls.health','ls.hub','ls.lgb','ls.lodef','ls.messagebus','misc','ops.n-liveservices-salt','ops.n-liveservices-salt-prod','rip.fms','rip.fms.asc','rip.fms.gateway','rip.fms.test','rip.wowza','rip.wowza.abr','rip.wowza.auth','rip.wowza.monitor','rip.wowza.transcodecontrol'],
    'UC':     ['atg-lodef','fci.selenium','fci.selenium.agents','hybrid.client','naiad.client.js','naiad.flash','naiad.thinflash'],
    'VM':     ['atg.pds','base-devel','caster-tv','cb-maila-salt','crm','debian-7.4','debian-crm','mg-maila-salt','n-maila-salt','skunkworks','vm.n-liveservices-salt-prod']
  }
  targetProject = False
  for project in projects:
    repolist = projects[project]
    if repoName in repolist:
      targetProject = project
      break

  return targetProject


def gitHash(repoPath):
  command = ['git', 'rev-parse', 'HEAD']

  return gitExecute(command, repoPath)


def gitPushed(repoPath):
  command = ['git', 'branch', '-r', '--contains']

  return len(gitExecute(command, repoPath)) != 0


def gitExecute(command, repoPath):
  execution = Popen(command, cwd=repoPath, stdout=PIPE, stderr=PIPE)
  (results, error) = execution.communicate()
  print(repoPath)
  if len(error) == 0:
    return results.decode('utf-8')
  else:
    return ""


# Return various paths to the file.
def getPaths(obj):
  projectFolders = obj.view.window().folders()
  path = obj.view.file_name()

  relativeToFolder = path # If outside of open folder, we'll just give absolute path
  repoName = ''
  relativeToRepo = ''
  pathToRepo = ''
  fileName = os.path.basename(path)

  # In the case that we have multiple folders open, find the one the file is in.
  for folder in projectFolders:
    if folder in path:
      relativeToFolder = path.replace(folder, '')[1:]
      repoName = relativeToFolder[:relativeToFolder.find('/')]
      relativeToRepo = relativeToFolder[len(repoName)+1:]
      pathToRepo = path[:-len(relativeToRepo)-1]
      break

  # Return a number of different file paths for various uses
  # ex: ['my.repo/dir/file.php', 'my.repo', 'dir/file.php', '/Users/me/git/my.repo', 'file.php']
  # If outside of folder structure, returns full path in first subarray
  return [relativeToFolder, repoName, relativeToRepo, pathToRepo, fileName]


# If more than one character is selected it will return a Stash line argument
def getLine(obj):
  if not obj.view.sel()[0].empty():
    (row,col) = obj.view.rowcol(obj.view.sel()[0].begin())
    return row+1
  else:
    return -1


# Stash link command
class CopyStashCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    paths = getPaths(self)

    if paths[1] == '':
      sublime.status_message("Stash URL Copy Failed: No repo name detected.")
      return

    targetProject = getProject(paths[1])

    if targetProject == False:
      sublime.status_message("Stash URL Copy Failed: Repo name \"%s\" not recognized." % paths[1])
      return

    line = getLine(self)
    hashID = gitHash(paths[3])

    pushed = gitPushed(paths[3])

    # Hash argument
    if hashID != "":
      if pushed:
        hashArgument = "?at=%s" % hashID
        hashMessage = " (linked to commit %s)" % hashID[:8]
      else:
        hashArgument = ""
        hashMessage = " (not linked to commit %s - it's not pushed!)" % hashID[:8]
    else:
      hashArgument = ""
      hashMessage = " (Problem with Git!?)"

    # Line argument
    lineArgument = "" if line <= 1 else "#%s" % str(line)
    lineMessage = "" if lineArgument == "" else " to line %s" % lineArgument

    url = 'https://stash.atg-corp.com/projects/%s/repos/%s/browse/%s%s%s' % \
    (targetProject, paths[1], paths[2], hashArgument, lineArgument)
    sublime.set_clipboard(url)
    sublime.status_message("Copied Stash URL%s%s" % (lineMessage, hashMessage))
    print("URL: %s" % url)


  def is_enabled(self):
    return bool(self.view.file_name() and len(self.view.file_name()) > 0)


# Relative path command
class CopyRelativePathCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    paths = getPaths(self)
    if paths[1] == '':
      message = "Copied absolute file path: %s"
    else:
      message = "Copied relative file path: %s"
    sublime.set_clipboard(paths[0])
    sublime.status_message(message % paths[0])


  def is_enabled(self):
    return bool(self.view.file_name() and len(self.view.file_name()) > 0)