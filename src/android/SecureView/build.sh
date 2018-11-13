#!/bin/bash

ant clean && ant debug &&
adb uninstall com.secure.view && adb install bin/SecureView-debug.apk
