---
title: "Reviving a 9-year-old HP laptop with Linux and hardware"
date: 2026-09-20
draft: true
url: "/laptop-revival/"
# headerImage: ".png"
# headerAlt: ""
---

I have a 2017 HP Pavilion 15-cc6xx, with an Intel i7-8550U (8th-gen) and 12GB RAM. This machine has been through a lot: it's what got me through my last 3 years of my Chemical Engineering degree, plus my first internship and job searches. I had replaced it with a Macbook Pro M1 back in 2022, so the HP has been sitting collecting dust for 5 years now!

I had actually tried out Linux before on a very old laptop while back in high school; it didn't go great as the hardware was even worse, I set it as dual-boot to keep Windows which caused problems, but most of all I just didn't keep at it long enough to get it to a great state.

This time around, I did a bit more research upfront, but most importantly, LLMs and coding agents exist now! I do a lot of compute cluster and infra work at work now, and LLMs/agents have of course completely changed the game from Googling and searching through forums to simply asking the agent. I know Linux has a similar problem profile of fiddly config knobs, so with agents it seemed like a great new opportunity to try it out. Spoiler - it went great! I've since been using Linux on the HP for a month now, for some personal projects, open-source work, and to type this and my previous blog post. 

---

## Linux Install: CachyOS

Linux distros are a persistently hot topic, and I don't have much new to add to that conversation. I chose CachyOS simply because it's built to be resource-efficient, and because being Arch-based, it seemed to have a bit more room for customizability. The other distro I closely considered was NixOS, for its ideas around reproducibility, declarative builds, and basically the whole idea of defining an "OS as code" (OSaC?), but alas it will wait for another day.

The CachyOS install itself was mostly uneventful. I opted to do a full wipe of the Windows installation for simplicity. The steps were standard:
- Backed up remaining files I wanted to keep from Windows
- Downloaded the CachyOS ISO onto a spare 32GB USB drive
- Booted the HP into the BIOS menu
- Disabled HP Secure Boot, then rebooted into BIOS again (CachyOS seemed to not support Secure Boot at least for my HP)
- Selected to boot Cachy from the USB
- Once booted into CachyOS in RAM, followed the installer to wipe the disk fully, create a fresh partition for only Linux, and install CachyOS into there
- Rebooted one last time, to finally get into the fresh disk install of CachyOS

I had a couple hiccups to figure it all out, including identifying Secure Boot as the reboot issue and getting the disk partitions right in the installer. But I was able to have an LLM walk me through the main steps and help me get unstuck at each stage.

In the CachyOS installer, it also prompts to pick a desktop environment. After a bit more research I chose [Xfce](https://www.xfce.org/), again just for its focus on simplicity and resource efficiency. I've come to really liking it; it beats Windows by miles (of course) but I think I even prefer its overall experience over MacOS.


## Linux Configuration and the Frozen Screen of Death




## SSD Upgrade

As I was debugging the frozen screen issue, and as I was just asking Grok/other models about the Linux install, one thing that came up with the slow disk speeds. It turns out this laptop was on a pretty budget HDD this entire time, and disk read speed was a huge bottleneck for basically every operation: boot times, app startup, file loading, etc. Memory swap was basically impossible, which explained why multitasking would always feel so sluggish back on Windows during my college days.

The coding agent figured out there was a spare, empty SSD slot in the laptop, and it measured the disk read speeds and used that to project that adding a basic M.2 SSD would speed up sequential reads by ~8-10x, and random reads (latency) by ~100x. HDD vs. SSD performance is a well-characterized topic, and every new mid and upper-tier laptop has certainly come with an SSD for many years, so it seemed like a nice upgrade. It sounds silly to be spending money upgrading a 9-year-old laptop, but I had already spent the time reinstalling the OS and was eager to make it daily driver-worthy, so I pulled the trigger on a [512GB Timetec M.2 SATA 2280 SSD](https://www.amazon.com/dp/B08GJDHMPB) from Amazon for $72.

Once it arrived, I took off the bottom cover and installed the SSD. This was pretty easy; I've done the same with replacing the SSD in my Steam Deck, so I did the same here (there are many online guides and videos).

After reboot, the OS was still installed only on the HDD. I asked Grok Build to find the new SSD and help me get the OS set up there, and it was able to figure it all out! From what I understand, it created a new drive object within the OS on the SSD, copied the entire OS and filesystem over from the HDD, and then it set the startup settings to boot onto the SSD instead. The boot settings did not work at first: it booted back onto the OS on HDD a couple times, then it landed on the SSD, then back on the HDD. Finally it was able to figure out the configs and get the SSD set permanently.

[pics]

Once booted onto the SSD, I was legitimately shocked at how much snappier everything is. Ghostty started in <1 second! Firefox in <2! I have a habit of constantly using Alt-Tab to switch across windows, and Ctrl + Space to open the App Finder, and those both seem to literally load instantly which makes a massive difference in OS feel. It blows my mind that I just accepted this sluggish performance on the HDD for my college years, using this for everything from Matlab projects to Python data analysis to [Aspen HYSYS](https://www.aspentech.com/en/products/engineering/aspen-hysys) (extremely heavyweight processing engineering modelling software, no idea how was able to run).

The HDD is still installed and holds the stale OS copy. I plan to wipe the OS there and then use the HDD as bulk storage, as it's a full 1TB of good functional storage, but I haven't gotten around to that yet.

For actual performance benchmarks, I did have the foresight to record some numbers before and after the upgrade:

[table]



## Battery Upgrade

The other hardware issue I figured out from Grok Build was the battery. I had always accepted that this HP laptop had terrible battery life; I broght the charging brick everywhere during school, and I memorized dozens of study spots across campus with outlet access. Anything more than a 1-2 hour study period and I knew the laptop battery wouldn't make it. 

The agent started out measuring average power draw around 5W, with heavy use going up to ~8-10W. With the design energy of 42Wh, and assuming a conservative 50-60% battery state of health after many years, that should be giving around 3 hours of mixed use battery life. But still, I was finding myself lucky to get even 1.5 hours, which measured up to ~15-20Wh of energy. Low and behold, the design capacity was being reported to the firmware as only 15.5Wh! Even on an old battery, this design capacity should report as the designed 42Wh. After a bit more debugging here, I'm still not 100% sure if the original battery was counterfeit (seems unlikely given the laptop was ordered from Costco), or if the battery just had major degradation and somehow had the capacity reproting reset maybe due to the OS switch. But it was clear a battery update was due if I wanted battery life to be reasonable.

Again, I ordered a new replacement online - a TF03XL part number pouch cell battery, and I chose one sold by brand GHU for $33, since it seemed to have good reviews and a legit website with many battery models for sale. It came in, I cracked open the cover again, and I replace the battery itself.

[image]

After reboot, it got stuck on a BIOS `Unauthenticated` error, until I figured out I had to re-disable Secure Boot due to the new hardware component being detected. After that it booted up healthy. I charged the battery up to 100%, then unplugged and used the laptop throughout the day down to 10%, with a background logger set up and running from my agent. And once again, this hardware upgrade did not disappoint: it gets 97% of the designed 42Wh energy (well within the range of a new battery). So it fully panned out, and so far it's looking like an extremely healthy 6+ hours of mixed use battery life. Again, an amazing upgrade compared to before, and I kicking myself for not trying this when I was actually using this laptop all the time in college!

[data]

## Performance Summary


## Conclusion