# [DESCRIPTION]

> A compilation of command line commands that I use/used to build this app.

## [TO create/generate a new project]:

`android create project --target 7 --name <PROJECT NAME> --path . --activity <ACTIVITY NAME> --package com.package.name`

> **NOTE:** This should be done from the root of the project directory.

## [LIST targets]:

`android list targets`

**Example**

```
[anthony@ghost JustDrive]$ android list targets

Available Android targets:

----------

id: 1 or "android-14"

     Name: Android 4.0

     Type: Platform

     API level: 14

     Revision: 4

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800

 Tag/ABIs : no ABIs.

----------

id: 2 or "android-15"

     Name: Android 4.0.3

     Type: Platform

     API level: 15

     Revision: 5

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800

 Tag/ABIs : no ABIs.

----------

id: 3 or "android-16"

     Name: Android 4.1.2

     Type: Platform

     API level: 16

     Revision: 5

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in

 Tag/ABIs : no ABIs.

----------

id: 4 or "android-17"

     Name: Android 4.2.2

     Type: Platform

     API level: 17

     Revision: 3

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in

 Tag/ABIs : no ABIs.

----------

id: 5 or "android-18"

     Name: Android 4.3.1

     Type: Platform

     API level: 18

     Revision: 3

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in

 Tag/ABIs : no ABIs.

----------

id: 6 or "android-19"

     Name: Android 4.4.2

     Type: Platform

     API level: 19

     Revision: 4

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in

 Tag/ABIs : no ABIs.

----------

id: 7 or "android-21"

     Name: Android 5.0.1

     Type: Platform

     API level: 21

     Revision: 2

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in

 Tag/ABIs : no ABIs.

----------

id: 8 or "android-22"

     Name: Android 5.1.1

     Type: Platform

     API level: 22

     Revision: 2

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in

 Tag/ABIs : no ABIs.

----------

id: 9 or "android-23"

     Name: Android 6.0

     Type: Platform

     API level: 23

     Revision: 3

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in, AndroidWearRound, AndroidWearRound360x360, AndroidWearRound400x400, AndroidWearRound480x480, AndroidWearRoundChin320x290, AndroidWearRoundChin320x300, AndroidWearRoundChin360x325, AndroidWearRoundChin360x326, AndroidWearRoundChin360x330, AndroidWearSquare, AndroidWearSquare240x240, AndroidWearSquare320x320

 Tag/ABIs : android-tv/armeabi-v7a, android-wear/armeabi-v7a

----------

id: 10 or "android-24"

     Name: Android 7.0

     Type: Platform

     API level: 24

     Revision: 2

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in

 Tag/ABIs : default/arm64-v8a, default/armeabi-v7a, google_apis/arm64-v8a, google_apis/armeabi-v7a

----------

id: 11 or "android-25"

     Name: Android 7.1.1

     Type: Platform

     API level: 25

     Revision: 3

     Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in

 Tag/ABIs : no ABIs.

----------
```

> **NOTE:** You want the ID that is of type "platform", not of type "addon"!

## [UPDATE project]

> **NOTE:** This mostly used when changing target number or deleting build.xml file

`android update project --name keySender --subprojects --target 14 --path .`

## [CLEAN the build]:

`ant clean`

> **NOTE:** This will not delete the build.mxl file but will delete the bin and gen directories.

## [BUILD app for non-production and testing purposes]:

`ant debug`

## [BUILD app for production and release]:

> **NOTE:** The app needs to be signed before you can build for production/release - See bottom on how to sign APK.

`ant release`


## [PUSHING app to phone via ADB]:

`adb push bin/JustDrive-debug.apk /sdcard/Download/`

## [DEBUG app crashes]:

`adb shell logcat | egrep --color -i runtime`

## [DEBUG code with max verbosity]:

> **NOTE:** This will show everything running on your phone with max verbosity set.

`adb shell logcat`

## [CREATE an AVD on the command line]:

`android create avd -n Nexus6_dev -t 9 -c 1024M -s 480x800`

## [LIST AVD's]:

`emulator -list-avds`

## [START AVD FROM COMMAND LINE]:

**Run one of the listed emulators:**

`emulator @name-of-your-emulator`

**Example:**

`emulator @nexus_dev`

...

**where emulator is under:**

${ANDROID_SDK}/tools/emulator

**Export env variable to prevent 32 deprication error:**

`export ANDROID_EMULATOR_FORCE_32BIT=true`

> **NOTE:** Add to .bashrc file!!

## [Signing an APK]:

> **NOTE:** Run this from the command line to generate a release key:

`keytool -genkey -v -keystore release.keystore -alias releasekey -keyalg RSA -keysize 2048 -validity 10000`

> **NOTE:** Add this to your ant.properties file. If you dont have one create one.

## [KEYSTORE with ant.properties]:

`key.store=release.keystore`

`key.alias=releasekey`

`key.store.password=my_password`

`key.alias.password=my_password`


## [PULL remote branch into local]:

`git fetch origin`

`git checkout --track -b <remote branch name> origin/<remote branch name>`

**Example** 

`git checkout --track -b JustDriveBranch4 origin/JustDriveBranch4`


## [ROLL back push/commit to specific branch]:

> **NOTE** This is for your local branches.

`git reset --hard <branch commit string>`

## [ROLL back push/commit to specific branch]:

> **NOTE:** This is for remote branches.

`git push -f origin <branch commit string:branch name>`

## [REMOVE unwanted added files]:

> **NOTE:** An example of having to use this would be after running "git add ."

`git rm -r <file or dir name>`

`git rm --cached -r <file or dir name>`

## [CHANGE java version]:
`sudo update-alternatives --config java`
