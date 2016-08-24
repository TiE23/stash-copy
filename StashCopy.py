import os
import re
from subprocess import Popen, PIPE
from platform import system
from json import load

import sublime
import sublime_plugin


def importJSON(fileName):
  # Need to be oddly explicit about the location of the file's path.
  filePath = "{}{}".format(__file__[:__file__.rfind("/")+1], fileName)

  with open(filePath, 'r') as jsonFileIn:
    jsonDict = {}
    jsonDict.update(load(jsonFileIn))

  return jsonDict

# Check known project names against reported repository name.
def getProject(repoName):
  projects = importJSON('projects.json')
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