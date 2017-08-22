import os
import re
from subprocess import Popen, PIPE
from platform import system

import sublime
import sublime_plugin

# Moved back here because sublime-packages don't really support .json files like
# I was doing before...
projects = {
  "ADNET": [
    "adconfigs",
    "adnet.clickidrelay.svc",
    "AdRouter",
    "AdRouterBase",
    "adserver",
    "atg_stats",
    "cachegenerator",
    "Console",
    "logsummarizer",
    "marketplaceapi",
    "marketplacelib",
    "marketplaceui",
    "sancdn.m",
    "sanshared",
    "sanslides",
    "sanstack",
    "tracker",
    "tracker2s"
  ],
  "CB": [
    "affinitycams.server",
    "bl.client.js",
    "bl.example.php",
    "blacklabel.webservice",
    "blacklabel.webservice.old",
    "blc.client",
    "blc.server",
    "blc.utils",
    "cambuilder.tools",
    "cambuilder.webservice",
    "cb.vm",
    "dev.aaron",
    "exampleblacklabel.client",
    "exampleblacklabel.server",
    "mh.admin",
    "mh.core",
    "mh.server",
    "naiad.cambuilder",
    "naiad.cambuilder.build",
    "naiad.cambuilder.homepage",
    "naiad.cambuilder.webapp",
    "naiad.sitebuilder"
  ],
  "ATTIC": [
    "adserver1.0",
    "atg-data",
    "auth.service",
    "authorization.admin",
    "authorization.api",
    "blc.prototype",
    "blc.prototype.router",
    "cb.cbreports.webapp",
    "cb.promotools.webapp",
    "cb.sitebuilder.webapp",
    "cb.sitewizard.webapp",
    "db.bi",
    "DollaBillZ",
    "dv.ffmpeg",
    "fci.selenium",
    "fci.selenium.agents",
    "hello_world",
    "icf-authn",
    "icf.core.client.js",
    "icf.xment.admin",
    "Javaloms",
    "kafkacreator.storm",
    "KafkaToPhp",
    "labe.naiad.fms",
    "labe.naiad.fms.asc",
    "labe.naiad.fms.gateway",
    "labe.naiad.fms.test",
    "lbe.health",
    "lbe.lgb",
    "lbe.lib.XmlStreamsServer.js",
    "lbe.lodef",
    "lodef",
    "ls.messagebus",
    "ls.messagebus-cluster",
    "ls.naiad.liveservices.gateway",
    "ls.naiad.liveservices.libs",
    "ls.naiad.liveservices.messagebus",
    "ls.segmenter",
    "ls.testrepo",
    "lte.ffmpeg.test",
    "lte.naiad.transcode.ffmpeg",
    "lte.naiad.transcode.host",
    "lte.naiad.transcode.queue",
    "lvd.naiad.wowza",
    "lvd.naiad.wowza.abr",
    "lvd.naiad.wowza.auth",
    "lvd.naiad.wowza.monitor",
    "lvd.naiad.wowza.transcodecontrol",
    "marketplaceapiold",
    "marketplacedesign",
    "marketplaceuiold",
    "misc",
    "nc.balance",
    "nc.helper",
    "nc.ipv4",
    "nc.platform",
    "PhpToKafka",
    "prower",
    "qa.play.with.git",
    "react.thinflash",
    "san.flash.as3",
    "scp.mobile",
    "scp.server",
    "sexadnet",
    "sexadnet.generated.configs",
    "sexadnet.qa",
    "splunk",
    "Storm Tools",
    "Storm Vagrant",
    "sw.atg.core.php",
    "sw.atg.lib.php",
    "sw.atg.service.phpdoc",
    "sw.naiad.lib.php",
    "sw.naiad.service.perfsearch",
    "sw.naiad.service.perfsearch.skin",
    "sw.svc.atg.example.nodejs",
    "sw.svc.atg.example.php",
    "ta.webservice",
    "tvbroadcast",
    "vm.n-liveservices-salt",
    "voltron",
    "xojo"
  ],
  "BIL": [
    "billing.history",
    "billing.prototype",
    "billing.storm",
    "fap.services",
    "icf.billing",
    "naiad.bling",
    "naiad.descriptorsites",
    "poc.billaccount.storm",
    "poc.chargecreated.storm",
    "poc.checkbalance.storm",
    "poc.collect.storm",
    "sdk.authn.python",
    "storm-docker",
    "storm-docker.old"
  ],
  "CM": [
    "blackbook.webapp",
    "blackbook.webservice",
    "gorilla",
    "gorilla-frontend",
    "itsup.webservice",
    "notifications.webservice",
    "senderella.bouncer",
    "senderella.client",
    "senderella.core",
    "senderella.unsubscribe",
    "senderella.webservice"
  ],
  "CORENODEJS": [
    "icf-core.nodejs"
  ],
  "CORE": [
    "admin.server",
    "alldbapi",
    "alldbapiphpclient",
    "auth.webservice",
    "etcatg.vault",
    "examplenodejs.webservice",
    "examplereact",
    "heartbeat.webservice",
    "icf.authn",
    "icf.core.java",
    "localdev.docker",
    "monitor.webservice",
    "storm-docker",
    "useragent.webservice",
    "volt.tool"
  ],
  "COREPHP":[
    "icf.core",
    "examplephp.webservice",
    "icf.coredeprecated",
    "sdk.auth.php",
    "sdk.loms.php",
    "sdk.xment.php"
  ],
  "CREA": [
    "creative.join"
  ],
  "DE": [
    "analytics.webservice",
    "connect.bigquery.kafka",
    "connectjdbc.kafka",
    "connectpubsub.kafka",
    "elasticsearchloms.storm",
    "icf.kafka",
    "icf.storm.java",
    "kafka.tools",
    "loms.webservice",
    "lomsrouter.storm",
    "xment.webservice"
  ],
  "TOOLS": [
    "atg-hipchat-hubot",
    "atg-hubot",
    "doggy",
    "echelon",
    "fci.make",
    "jenkins-config",
    "jenkins-config-sg",
    "multipass",
    "naiad.internal",
    "networkshaper",
    "schnauzer",
    "senderella-scripts",
    "staging",
    "users",
    "wallboard"
  ],
  "DOPS": [
    "environmentmonitor.webservice",
    "icf.compose.deploy",
    "icf.compose.jenkins",
    "icf.devbase",
    "icf.docker.apache.php",
    "icf.docker.availperf.redis",
    "icf.docker.curator",
    "icf.docker.elasticsearch",
    "icf.docker.elk",
    "icf.docker.filebeat",
    "icf.docker.grafana",
    "icf.docker.java",
    "icf.docker.kafka",
    "icf.docker.kibana",
    "icf.docker.logstash",
    "icf.docker.mongodb",
    "icf.docker.mysql",
    "icf.docker.nginx",
    "icf.docker.node",
    "icf.docker.nodejs",
    "icf.docker.nodejs.lite",
    "icf.docker.postgresql",
    "icf.docker.proxy",
    "icf.docker.redis",
    "icf.docker.site-proxy",
    "icf.docker.smalldb",
    "icf.docker.statsd",
    "icf.docker.statsd.gce",
    "icf.docker.storm",
    "icf.docker.storm2",
    "icf.docker.tomcat",
    "icf.docker.zookeeper",
    "icf.localdev",
    "pipeline.jenkins",
    "tools"
  ],
  "DV": [
    "dv.coturn",
    "dv.ffmpeg-wrapper",
    "dv.hoodwatch",
    "dv.janus",
    "dv.transcode",
    "dv.transcode.queue",
    "ls.lgb",
    "ls.lodef",
    "videoencoder.webservice"
  ],
  "ENC": [
    "enc.android",
    "enc.atg-qt5",
    "enc.control.service",
    "enc.control.service.mobile.mock",
    "enc.crashreport.service",
    "enc.desktop",
    "enc.dist",
    "enc.ios",
    "enc.ios.logging",
    "enc.performer.ffmpeg",
    "enc.sfu.mediasoup",
    "performer.streamingcenter"
  ],
  "HACK": [
    "2016_Q2_hackathon-achievements",
    "achievements.webservice",
    "activityfeed.webservice",
    "bonerchat.client",
    "bonerchat.webservice",
    "ExtremeStream",
    "fraudprevention",
    "notification.webservice",
    "pantygnome",
    "pantygnome.prototype",
    "streamrtc.server",
    "userinterests.webservice",
    "workshop2"
  ],
  "IS": [
    "huginn",
    "inventory-bt5"
  ],
  "MEMB": [
    "icf.membership"
  ],
  "MOB": [
    "android.livecamapp",
    "android.livecamapp.jenkinstest",
    "android.livecamapp.release",
    "android.livecamappcontrol",
    "ios.bline"
  ],
  "NC": [
    "fci.ext",
    "fci.perl",
    "fci.php",
    "fci.sauth",
    "maxmind",
    "merlin",
    "naiad.core",
    "naiad.exports",
    "naiad.gfx",
    "naiad.web"
  ],
  "NODE": [
    "atg-appconfig",
    "atg-balance",
    "atg-bl-streamtest",
    "atg-cluster-master",
    "atg-fileconfig",
    "atg-helper",
    "atg-ipv4",
    "atg-js-styleguide",
    "atg-log",
    "atg-node-skeleton",
    "atg-platform",
    "atg-s2-e2etest",
    "atg-service-control",
    "atg-service-wrapper",
    "atg-transcode-process",
    "atg-uuid",
    "atg-wdio-config",
    "atg-xmlstreamserver",
    "icf-analytics",
    "icf-loms",
    "icf-performance-timing",
    "icf-request-cache",
    "icf-tracking",
    "icf-tracking-middleware",
    "icf.react.components",
    "libs"
  ],
  "UC": [
    "hybrid.client",
    "naiad.client.js",
    "naiad.flash",
    "naiad.thinflash",
    "pure.client",
    "splunk-elasticsearch",
    "streamconfig.webservice"
  ],
  "SM": [
    "naiad.css",
    "naiad.producer",
    "naiad.site",
    "naiad.site.deprecated",
    "naiad.skin",
    "naiad.streamate",
    "naiad.webapp.streamate",
    "preference.webservice",
    "sdet.tools",
    "streamate.react.rollover",
    "streamate.server",
    "streamate.signup.iframe.css"
  ],
  "PM": [
    "db.live",
    "splunk"
  ],
  "PSUP": [
    "bradmin"
  ],
  "PROTO": [
    "3dvision.silverlight",
    "fuqt",
    "googleglass",
    "hworld",
    "liveservices.translate",
    "quality-code-testing-js",
    "rad.modelservices.encoder",
    "rad.webrtc",
    "realman",
    "streamatedesktop.tide",
    "test"
  ],
  "QA": [
    "membership.robot",
    "oneclickjoin.robot",
    "qa.atg.robot",
    "SMM.robot",
    "streamate.robot",
    "streaming.robot"
  ],
  "SS": [
    "availperf.redis",
    "datascience.datalab",
    "datascience.models",
    "handyperf",
    "location.webservice",
    "search.api",
    "search.pipeline"
  ],
  "SMM": [
    "flare",
    "inmail.webservice",
    "modelmedia",
    "naiad.smm",
    "performer.api",
    "performer.webservice",
    "performerdesktop.tide",
    "smmoauth",
    "TideSDK",
    "vhs.api",
    "videoupload.webservice"
  ],
  "SG": [
    "ls.health",
    "ls.hub",
    "ops.containers",
    "ops.docker-deployer",
    "ops.i-liveservices-salt",
    "ops.n-liveservices-salt",
    "ops.n-liveservices-salt-prod",
    "ops.packer",
    "rip.fms",
    "rip.fms.asc",
    "rip.fms.gateway",
    "rip.fms.test",
    "rip.wowza",
    "rip.wowza.abr",
    "rip.wowza.auth",
    "rip.wowza.monitor",
    "rip.wowza.transcodecontrol",
    "streaming.webservice",
    "streamtracker.webservice",
    "videoprocessor.webservice",
    "vm.ad-streaming-service",
    "vm.atg-canvas-player"
  ],
  "TA": [
    "aiwtest.server",
    "apitest.blacklabel",
    "guitest.all-in-wonder",
    "guitest.pornhub",
    "guitest.smm",
    "guitest.streamate",
    "testperformer.webservice"
  ],
  "VM": [
    "atg.pds",
    "base-devel",
    "caster-tv",
    "cb-maila-salt",
    "crm",
    "debian-7.4",
    "debian-crm",
    "mg-maila-salt",
    "n-maila-salt",
    "skunkworks",
    "vm.n-liveservices-salt-prod"
  ],
  "WEB": [
    "webrtc.server"
  ]
}

# Check known project names against reported repository name.
def getProject(repoName):
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