import os
import re

import sublime
import sublime_plugin

class CopyStashCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    projectFolders = self.view.window().folders()
    self.path = self.view.file_name()
    for folder in projectFolders:
      if folder in self.view.file_name():
        self.path = self.path.replace(folder, '')[1:]
        break

    matches = re.match(r"^([^\/]*)(.*)", self.path).groups()

    if len(matches) != 2:
      sublime.status_message("Stash URL Copy Failed: %s" % self.path)
      return

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
    targetProject = 'UNKNOWN'
    for project in projects:
      repolist = projects[project]
      if matches[0] in repolist:
        targetProject = project
        break

    url = 'https://stash.atg-corp.com/projects/%s/repos/%s/browse%s' % (targetProject, matches[0], matches[1]);
    sublime.set_clipboard(url)
    sublime.status_message("Stash URL: %s" % url)

  def is_enabled(self):
      return bool(self.view.file_name() and len(self.view.file_name()) > 0)