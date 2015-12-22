# stash-copy
## Summary
Sublime 2/3 Plugin that'll generate **Stash URL links** to any source file you've got open.

**_It's useful._**

Share the file you're looking at on **any line**, on **any commit** in just one keystroke.

### Features
- Automatically include the Git commit ID in your URL.
- Include a line number shortcut in your URL.
- Copy relative-path to any file.

### When to use it
- Jira comments! "_The problem is right here._"
- Sanity checks over IM! "_Can you believe this?!_"
- Ad-hoc code reviews! "_It's not ready for a pull request yet but..._"

**Custom made for my co-workers at ATG.**

## Functionality
### Keyboard Shortcuts (OSX Examples)
- CMD+SHIFT+C (Folder Open in Sublime)
  - Copy file path relative to your main git folder.
  - Example: "my.repo/README"
- CMD+SHIFT+C (File Open Outside of Folder)
  - Copy absolute file path.
  - Example: "/Users/me/myfile.txt"
- CMD+SHIFT+X
  - Copy a link to Stash
  - Example: "https://stash.example.com/projects/AA/repos/my.repo/browse/README"
- CMD+SHIFT+X (Line is high-lighted)
  - Copy a link to Stash at the selected line number
  - Example: "https://stash.example.com/projects/AA/repos/my.repo/browse/README#42"
- CMD+ALT+X
  - Copy a link to Stash with current Git commit ID
  - Example: "https://stash.example.com/projects/AA/repos/my.repo/browse/README?at=596f7527766520676f7420667265652074696d65"
- CMD+ALT+X (Line is high-lighted)
  - Copy a link to Stash with current Git commit ID at the selected line number
  - Example: "https://stash.example.com/projects/AA/repos/my.repo/browse/README?at=596f7527766520676f7420667265652074696d65#42"

### Command Palette Shortcuts
These shortcuts and also be found in the command pallet as "Copy URL to Stash Page" and "Copy URL to Stash Page w/ Git Commit".

### Context Menu Shortcuts
Right clicking on an open file will reveal the same commands: "Copy URL to Stash Page" and "Copy URL to Stash Page w/ Git Commit".

### File Tab Context Menu Shortcuts
Right clicking on a file tab will reveal the same commands: "Copy URL to Stash Page" and "Copy URL to Stash Page w/ Git Commit" with keyboard shortcut reminders.

## Installing
1. Install Sublime Package Control following [this guide](https://packagecontrol.io/installation) (takes less than 30 seconds).
2. When that's installed copy this URL: https://github.com/TiE23/stash-copy.git
3. In Sublime hit Cmd+Shift+P (Ctrl+Shift+P on Windows) and type in "Package Control", select "Package Control: Add Repository"
4. Paste in the URL to the little text entry that pops up at the bottom and hit enter.
5. Cmd+Shift+P (Ctrl+Shift+P on Windows) and type in "Package Control", select "Package Control: Install Package"
6. Type in "stash-copy" and hit enter.

### Directory Structure Requirements
Be sure that all your open repositories reside in a single directory such as ~/git and not inside any other directories.

```
# Good
~/git
~/git/repo.01
~/git/repo.02
~/git/repo.03

# Bad
~/git
~/git/frontend/repo.01
~/git/frontend/repo.02
~/git/backend/repo.03
```

In Sublime open the entire ~/git directory and do your work from there.

_Future feature_: Relax or remove this requirement...

### Repo Name Requirement
It will fail if your repo name is wrong. Keep the names of the repos the way they are!

### Notes on Git Functionality
Keep an eye on the status bar on the bottom of the window when using this tool.
- It will warn you if you attempt to copy a git commit with a commit that isn't tracked remotely (not pushed).
- It will warn you if you attempt to copy a line number with a modified file (buffer or git are dirty).
- It might pause for a moment when doing Git-stuff if your git repo is very large and slow. Sorry about that.

# Copyright
This software is licensed under the Hogwarts School of Witchcraft and Wizardry License. ¯\\\_(ツ)\_/¯