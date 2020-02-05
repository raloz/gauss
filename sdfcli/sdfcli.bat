@ECHO off

set supported_java_version=1.8
set cli_jar_file_name=cli-2019.2.1.jar

set msg_java_not_installed=Java Runtime Environment is not installed on this machine. Install JRE version %supported_java_version% to run SDF CLI.
set msg_java_incompatible_version=Your Java version is not compatible with SDF CLI. Install JRE version %supported_java_version%.
set msg_jar_file_missing=The JAR file could not be found. Download the JAR file from the Help Center into the same directory where the SDF CLI script is stored.

java -version 1>nul 2>nul || (
   echo %msg_java_not_installed%
   exit /b 1
)
for /f tokens^=2-5^ delims^=^" %%j in ('java -fullversion 2^>^&1') do set "installed_java_version=%%j%%k%%l%%m"

if not "%installed_java_version:~0,3%" == "%supported_java_version%" (
	echo %msg_java_incompatible_version%
	exit /b 1
)

set cli_directory=%~dp0
set cli_jar_file_path="%cli_directory%%cli_jar_file_name%"

if not exist %cli_jar_file_path% (
    echo %msg_jar_file_missing%
	exit /b 1
)

java -jar %cli_jar_file_path% %*
