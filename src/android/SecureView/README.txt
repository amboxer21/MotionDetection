A compilation of command line commands that I use/used to build this app.

TO CREATE/GENERATE A NEW PROJECT:
android create project --target 14 --name <PROJECT NAME> --path . --activity <ACTIVITY NAME> --package com.package.name

TO LIST TARGETS:
android list targets

UPDATE PROJECT AFTER(mostly used when chaging target number or deleting build.xml file:
android update project --name keySender --subprojects --target 14 --path .

CLEAN BUILD:
ant clean

BUILD APP for debug:
ant debug

BUILD APP for release(Needs to be signed - See bottom on how to sign APK):

PUSH:
adb push bin/JustDrive-release.apk /sdcard/Download/

DEBUG CRASHES:
adb shell logcat | egrep --color -i runtime

DEBUG CODE:
adb shell logcat

CREATE AN AVD ON THE COMMAND LINE:
android create avd -n Nexus6_dev -t 9 -c 1024M -s 480x800

LIST AVD's:
emulator -list-avds

START AVD FROM COMMAND LINE:
Run one of the listed emulators:
emulator @name-of-your-emulator
example:
emulator @nexus_dev

...
where emulator is under:
${ANDROID_SDK}/tools/emulator

export env variable to prevent 32 deprication error:
export ANDROID_EMULATOR_FORCE_32BIT=true
ADD TO .bashrc file.

Building an APK for release : ant release
Signing an APK:

Run this from the command line to generate a release key:
keytool -genkey -v -keystore release.keystore -alias releasekey -keyalg RSA -keysize 2048 -validity 10000

Add this to your ant.properties file. If you dont have one create one. :

key.store=release.keystore
key.alias=releasekey
key.store.password=my_password
key.alias.password=my_password


pull remote branch into local:
git fetch origin
git checkout --track -b <rmote branch name> origin/<remote branch name>

Example:
git checkout --track -b JustDriveBranch4 origin/JustDriveBranch4

Delete a local branch:
git branch -d <branch name>

Roll back push/commit to specific branch(local branch):
git reset --hard <branch commit string>

Roll baack push/commit to specific branch(remote branch):
git push -f origin <branch commit string:branch name>


Remove unwanted added files(git add .):
git rm -r <file or dir name>
git rm --cached -r <file or dir name>

Change java version:
sudo update-alternatives --config java


If you deleted your build.xml file:
android update project -p /home/anthony/Documents/Python/MotionDetection/src/android/SecureView/

List packages to install:
/home/anthony/Documents/ZIPs/cmdline-tools/bin/sdkmanager --list --sdk_root="/home/anthony/android-sdk-linux"

Install platform tools:
/home/anthony/Documents/ZIPs/cmdline-tools/bin/sdkmanager "platform-tools" "platforms;android-30" --sdk_root="/home/anthony/android-sdk-linux"

Install build tools:
/home/anthony/Documents/ZIPs/cmdline-tools/bin/sdkmanager "platform-tools" "build-tools;30.0.0" --sdk_root="/home/anthony/android-sdk-linux"
