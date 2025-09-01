---
title: "A simple Git alias setup"
date: 2025-08-31
draft: false
---

Here are three simple but useful Git shortcuts that I use dozens of times a day.

TLDR: Add these to your `.bashrc` or `.zshrc`:

```bash
alias gs='git status -sb'
alias glog="git log --graph --pretty=format:'%Cred%h%Creset %an: %s - %Creset %C(yellow)%d%Creset %Cgreen(%cr)%Creset' --abbrev-commit --date=relative"
```


### 1. `gs`: Git Status
```bash
gs
```
![gs output](image.png)

### 2. `glog`: Git Log Graph

```bash
glog
```
![alt text](image-1.png)



### 3. `ga/gc/gp`: Add/Commit/Push

```bash
ga content/posts/
gc -m "Add git shortcuts post"
gp
```




There are many online resources with more comprehensive setups, but the ones below strike the right balance for me. Others that are interesting: 
- [Must-Have Git Aliases](https://www.durdn.com/blog/2012/11/22/must-have-git-aliases-advanced-examples/)
- [Ultimate Git Alias Setup](https://gist.github.com/mwhite/6887990)