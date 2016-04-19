import os
import re
from subprocess import Popen, PIPE
from platform import system

import sublime
import sublime_plugin


# Check known project names against reported repository name.
def getProject(repoName):
  projects = {
    'ADNET':  ['adconfigs','AdRouter','AdRouterBase','adserver','atg_stats','cachegenerator','Console','logsummarizer','marketplaceapi','marketplacelib','marketplaceui','sancdn.m','sanshared','sanslides','sanstack','tracker','tracker2s'],
    'ADBREP': ['alldbapi','alldbapiphpclient'],
    'ATTIC':  ['adserver1.0','cb.cbreports.webapp','cb.promotools.webapp','cb.sitebuilder.webapp','cb.sitewizard.webapp','DollaBillZ','dv.ffmpeg','labe.naiad.fms','labe.naiad.fms.asc','labe.naiad.fms.gateway','labe.naiad.fms.test','lbe.health','lbe.lgb','lbe.lib.XmlStreamsServer.js','lbe.lodef','lodef','ls.naiad.liveservices.gateway','ls.naiad.liveservices.libs','ls.naiad.liveservices.messagebus','ls.testrepo','lte.ffmpeg.test','lte.naiad.transcode.ffmpeg','lte.naiad.transcode.host','lte.naiad.transcode.queue','lvd.naiad.wowza','lvd.naiad.wowza.abr','lvd.naiad.wowza.auth','lvd.naiad.wowza.monitor','lvd.naiad.wowza.transcodecontrol','marketplaceapiold','marketplacedesign','marketplaceuiold','nc.balance','nc.helper','nc.ipv4','nc.platform','react.thinflash','san.flash.as3','sexadnet','sexadnet.generated.configs','sexadnet.qa','sw.atg.core.php','sw.atg.lib.php','sw.atg.service.phpdoc','sw.naiad.lib.php','sw.naiad.service.perfsearch','sw.naiad.service.perfsearch.skin','sw.svc.atg.example.nodejs','sw.svc.atg.example.php','vm.n-liveservices-salt'],
    'BIL':    ['billing.history','billing.prototype','fap.services','icf.billing','naiad.bling','naiad.descriptorsites'],
    'BLC':    ['bic.client','bic.prototype','bic.prototype.router','bic.server','bic.utils'],
    'CB':     ['cambuilder.tools','cb.vm','naiad.cambuilder','naiad.cambuilder.build','naiad.cambuilder.homepage','naiad.cambuilder.webapp','naiad.sitebuilder'],
    'CM':     ['gorilla','gorilla-frontend'],
    'TV':     ['naiad.producer','tvbroadcast','xojo'],
    'CREA':   ['creative.join'],
    'DB':     ['db.bi','db.live'],
    'TOOLS':  ['atg-hubot','doggy','echelon','fci.make','jenkins-config','naiad.internal','networkshaper','schnauzer','senderella-scripts','splunk','staging','users','wallboard'],
    'ICF':    ['icf.core','icf.core.js','icf.core.pds','icf.example.app.php','icf.example.build','icf.loms','icf.loms.pds','icf.xment','icf.xment.admin'],
    'INS':    ['auth.service','authorization.admin','authorization.api'],
    'MEMB':   ['icf.membership'],
    'MOB':    ['android.livecamapp','android.livecamapp.jenkinstest','android.livecamapp.release','android.livecamappcontrol','ios.bline'],
    'MH':     ['mh.admin','mh.core','mh.server'],
    'NC':     ['fci.ext','fci.perl','fci.php','fci.sauth','maxmind','merlin','naiad.core','naiad.exports','naiad.gfx','naiad.web'],
    'NODE':   ['atg-appconfig','atg-balance','atg-bl-streamtest','atg-cluster-master','atg-fileconfig','atg-helper','atg-ipv4','atg-js-styleguide','atg-log','atg-node-skeleton','atg-platform','atg-s2-e2etest','atg-service-control','atg-service-wrapper','atg-transcode-process','atg-xmlstreamserver','libs'],
    'PROTO':  ['3dvision.silverlight','fuqt','googleglass','hworld','liveservices.translate','rad.modelservices.encoder','rad.webrtc','realman','streamatedesktop.tide'],
    'SDK':    ['sdk.auth.php'],
    'SS':     ['availperf.redis','search.api'],
    'QA':     ['cambuilder.robot','membership.robot','qa.apitest','qa.common','streamate.robot'],
    'SS':     ['atg.core.php','atg.lib.php','atg.service.phpdoc','naiad.lib.php','naiad.service.perfsearch','naiad.service.perfsearch.skin','svc.atg.example.nodejs','svc.atg.example.php'],
    'SM':     ['naiad.css','naiad.site','naiad.site.deprecated','naiad.skin','naiad.streamate','naiad.webapp.streamate','sdet.tools'],
    'SMP':    ['streamate.mobile'],
    'SMM':    ['flare','modelmedia','naiad.smm','performerdesktop.tide','smmoauth','TideSDK'],
    'SG':     ['dv.ffmpeg-wrapper','dv.hoodwatch','dv.transcode','dv.transcode.queue','enc.android','enc.atg-qt5','enc.control.service','enc.control.service.mobile.mock','enc.control.service.mock','enc.desktop','enc.ios','ls.health','ls.hub','ls.hub-cluster','ls.lgb','ls.lodef','ls.messagebus','ls.messagebus-cluster','ls.segmenter','misc','ops.containers','ops.n-liveservices-salt','ops.n-liveservices-salt-prod','rip.fms','rip.fms.asc','rip.fms.gateway','rip.fms.test','rip.wowza','rip.wowza.abr','rip.wowza.auth','rip.wowza.monitor','rip.wowza.transcodecontrol'],
    'UC':     ['atg-data','atg-lodef','atg-mjpeg-player','atg-segment-streamer','fci.selenium','fci.selenium.agents','hybrid.client','naiad.client.js','naiad.flash','naiad.thinflash'],
    'VM':     ['atg.pds','base-devel','caster-tv','cb-maila-salt','crm','debian-7.4','debian-crm','mg-maila-salt','n-maila-salt','skunkworks','vm.n-liveservices-salt-prod']
  }
  targetProject = False
  for project in projects:
    repolist = projects[project]
    if repoName in repolist:
      targetProject = project
      break

  return targetProject


if system() == "Windows":
  slash = "\\"
else:
  slash = "/"

# Get the Git Commit Hash ID
def gitHash(repoPath):
  command = ['git', 'rev-parse', 'HEAD']

  return simpleShellExecute(command, repoPath)


# Check if the current commit has been pushed / is tracked
def gitPushed(repoPath):
  command = ['git', 'branch', '-r', '--contains']

  return len(simpleShellExecute(command, repoPath)) != 0


# Check if the current file is recognized by git as different. Do this by grepping the diff file list
def gitDirty(repoPath, fileName):
  p1 = Popen(['git', 'diff', '--name-only'], cwd=repoPath, stdout=PIPE, stderr=PIPE)
  p2 = Popen(['grep', fileName], cwd=repoPath, stdin=p1.stdout, stdout=PIPE, stderr=PIPE)

  return len(p2.communicate()[0].decode('utf-8')) != 0


def simpleShellExecute(command, executePath):
  execution = Popen(command, cwd=executePath, stdout=PIPE, stderr=PIPE)
  (results, error) = execution.communicate()

  if len(error) == 0:
    return results.decode('utf-8').strip()
  else:
    return ""


# Return various paths to the file.
# Return a number of different file paths for various uses.
# Ex: If a file's full path is /Users/me/git/my.repo/dir/file.php, you will get the following:
#    ['my.repo/dir/file.php', 'my.repo', 'dir/file.php', '/Users/me/git/my.repo', 'file.php']
# --- File with Repo -------- Repo Name - File no Repo ------ Repo location ------ File Name
# If outside of folder structure, returns full path in first subarray.
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
      repoName = relativeToFolder[:relativeToFolder.find(slash)]
      relativeToRepo = relativeToFolder[len(repoName)+1:]
      pathToRepo = path[:-len(relativeToRepo)-1]
      break

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

  def run(self, edit, gitEnabled=False, jiraLink=False):
    paths = getPaths(self)

    if paths[1] == '':
      sublime.status_message("Stash URL Copy Failed: No repo name detected.")
      return

    targetProject = getProject(paths[1])

    if targetProject == False:
      sublime.status_message("Stash URL Copy Failed: Repo name \"%s\" not recognized." % paths[1])
      return

    # Line argument
    line = getLine(self)
    lineArgument = "" if line <= 1 else "#%s" % str(line)
    lineMessage = "" if lineArgument == "" else " to line %s" % lineArgument

    # Git business
    if gitEnabled:
      hashID = gitHash(paths[3])
      pushed = gitPushed(paths[3])
      suspect = not pushed or self.view.is_dirty() or gitDirty(paths[3], paths[4])

      # Hash argument
      if hashID != "":
        if pushed:
          # The current commit is pushed, so we can link to it.
          hashArgument = "?at=%s" % hashID
          hashMessage = " (linked to commit %s)" % hashID[:8]
        else:
          # Commit isn't pushed, don't bother linking - people cannot view it.
          hashArgument = ""
          hashMessage = " (not linked to commit %s - it's not pushed!)" % hashID[:8]
      else:
        # Git returned nothing in stdout - problem?
        hashArgument = ""
        hashMessage = " (Problem with Git!?)"
    else:
      # Not doing Git stuff
      hashArgument = ""
      hashMessage = ""
      suspect = self.view.is_dirty()

    # Warn the user if the file is dirty (buffer or git is dirty) or commit is not pushed
    if suspect and lineArgument != "":
      lineMessage += " <--might be wrong!"

    url = 'https://stash.atg-corp.com/projects/%s/repos/%s/browse/%s%s%s' % \
    (targetProject, paths[1], paths[2], hashArgument, lineArgument)

    if jiraLink:
      if gitEnabled:
        linkText = "%s%s (%s)" % (paths[0], lineArgument, hashArgument[4:12])
      else:
        linkText = "%s%s" % (paths[0], lineArgument)

      clipBoard = "[%s|%s]" % (linkText, url)
      message = "Jira Link copied"
    else:
      clipBoard = url
      message = "Stash URL copied"

    sublime.set_clipboard(clipBoard)
    sublime.status_message("%s%s%s" % (message, lineMessage, hashMessage))

    print("Clipboard: %s" % clipBoard)


  def is_enabled(self):
    return bool(self.view.file_name() and len(self.view.file_name()) > 0)


# Variation of CopyStashCommand with Git-goodness
class CopyStashWithGit(sublime_plugin.TextCommand):
  def run(self, edit):
    CopyStashCommand.run(self, edit, True, False)

  def is_enabled(self):
    return CopyStashCommand.is_enabled(self)

# Variation of CopyStashCommand with Jira-goodness
class CopyStashWithJiraLink(sublime_plugin.TextCommand):
  def run(self, edit):
    CopyStashCommand.run(self, edit, False, True)

  def is_enabled(self):
    return CopyStashCommand.is_enabled(self)

# Variation of CopyStashCommand with Jira+Git-goodness
class CopyStashWithJiraLinkWithGit(sublime_plugin.TextCommand):
  def run(self, edit):
    CopyStashCommand.run(self, edit, True, True)

  def is_enabled(self):
    return CopyStashCommand.is_enabled(self)

# Relative path command
class CopyRelativePathCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    paths = getPaths(self)
    if paths[1] == '':
      message = "Copied absolute file path: %s"
    else:
      message = "Copied relative file path: %s"

    clipBoard = paths[0]
    sublime.set_clipboard(clipBoard)
    sublime.status_message(message % paths[0])

    print("Clipboard: %s" % clipBoard)

  def is_enabled(self):
    return bool(self.view.file_name() and len(self.view.file_name()) > 0)