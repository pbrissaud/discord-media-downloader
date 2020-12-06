from bs4 import BeautifulSoup
import requests
import os
import sys
import docker
import getopt
from pathlib import Path


def main(argv):
    global _verbose
    _verbose = False
    inputFilePath = ""
    outputDirectory = ""
    token = ""
    channelsDict = {}
    try:
        opts, _ = getopt.getopt(
            argv, "hi:t:o:v", ["help", "input=", "token=", "output=", "verbose"]
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-v", "--verbose"):
            _verbose = True
            print("INFO  --- Verbose mode is active")
        elif opt in ("-i", "--input"):
            inputFilePath = arg
        elif opt in ("-o", "--output"):
            outputDirectory = arg
        elif opt in ("-t", "--token"):
            token = arg

    # Check if inputFile is specified, exists and valid
    # If OK contruct the dictionnary
    if inputFilePath == "":
        print("ERROR --- Please specify the channel list's file in parameter")
        usage()
        sys.exit(2)

    if not os.path.exists(inputFilePath):
        print("ERROR --- The input file specified in parameter doesn't exist")
        sys.exit(3)

    if not os.path.isfile(inputFilePath):
        print("ERROR --- The input file specified in parameter isn't a file")
        sys.exit(4)

    with open(inputFilePath) as inputFile:
        for line_number, line in enumerate(inputFile, 1):
            try:
                key, value = line.split(":")
            except ValueError:
                print("ERROR --- Incorrect entry at line " + str(line_number) + " of input file : No ':' found")
                sys.exit(5)
            value = value.rstrip()
            if value == "":
                print("ERROR --- Incorrect entry at line " + str(line_number) + " of input file : Empty channel ID")
                sys.exit(5)
            channelsDict[key.strip().replace(" ", "_")] = value.strip()

    # Check outputDirectory, create folder in pwd if not specified
    pwd = os.path.dirname(os.path.realpath(__file__))
    if outputDirectory == "":
        Path(pwd + "/export/").mkdir(exist_ok=True)
        outputDirectory = pwd + "/export/"
        print("INFO  --- Output directory not specified, create 'export' folder in ", pwd) \
            if _verbose is True else None
    else:
        if not os.path.exists(outputDirectory):
            print("ERROR --- The output directory specified in parameter doesn't exist")
            sys.exit(6)
        if not os.path.isdir(outputDirectory):
            print("ERROR ---  The output directory specified in parameter isn't a directory")
            sys.exit(7)
        if outputDirectory[-1] != "/":
            outputDirectory = outputDirectory + "/"

    # Get Discord token from env_variable if not specified in parameter
    if token == "":
        print("INFO  --- The Discord token wasn't specified in parameter, searching in env DISCORD_TOKEN") \
            if _verbose is True else None
        token: str = os.getenv("DISCORD_TOKEN")
        if token is None:
            print("ERROR --- The Discord token wasn't specified either in parameter or in environnement variable")
            usage()
            sys.exit(8)

    run(token, channelsDict, outputDirectory)


def run(discordToken, channelsDict, outputDirectory):

    # Initialze Docker client
    client = docker.from_env()

    # Create tmp directory
    Path("/tmp/export-discord/").mkdir()

    for channelName, channelID in channelsDict.items():
        print("INFO  --- Exporting " + channelName + " channel (id=" + channelID + ")")

        # Create dest folder
        Path(outputDirectory + channelName).mkdir(parents=True, exist_ok=True)

        # Launch tyrrrz/discordchatexporter container
        # https://github.com/Tyrrrz/DiscordChatExporter/
        client.containers.run(
            "tyrrrz/discordchatexporter:stable",
            "export -t " + discordToken + " -c " + channelID,
            detach=False,
            remove=True,
            volumes={"/tmp/export-discord/": {"bind": "/app/out", "mode": "rw"}},
        )

        _, _, files = next(os.walk("/tmp/export-discord/"))
        if len(files) == 0:
            print("ERROR --- The container didn't export the channel, meaning that your token or the channel id is invalid")
            Path("/tmp/export-discord").rmdir()
            sys.exit(9)

        sourceFile = open("/tmp/export-discord/" + files[0], "r")
        soup = BeautifulSoup(sourceFile, "html.parser")
        attachementDivs = soup.find_all("div", class_="chatlog__attachment")
        print("INFO  --- Found " + str(len(attachementDivs)) + " medias in channel " + channelName)
        i = 0
        for div in attachementDivs:
            link = div.a.get("href")
            attachement = link[(link.rindex("/") + 1):]
            path = outputDirectory + channelName + "/" + attachement
            if not os.path.exists(path):
                i = i + 1
                with open(path, "wb") as f:
                    print("INFO  --- Downloading ", attachement) \
                        if _verbose is True else None
                    f.write(requests.get(link).content)

        print("INFO  --- " + str(i) + " medias were downloaded")
        os.remove("/tmp/export-discord/" + files[0])

    print("INFO  --- Export successfully completed")
    print("INFO  --- Files are located in " + outputDirectory)
    Path("/tmp/export-discord").rmdir()


def usage():
    print("\nUsage: python3 main.py [OPTIONS]")
    print("\nOPTION\t\tREQUIRED\tDESCRIPTION")
    print("-h, --help\tNO\t\tShow manual")
    print("-i, --input\tYES\t\tPath to config file\n\t\t\t\tTo know how to create this file, visit https://github.com/pbrissaud/discord-attachements-exporter/wiki/Usage-guide#create-your-config-file")
    print("-o, --output\tNO\t\tPath to directory where attachements will be downloaded ; if not specified, the script will create one in pwd")
    print("-t, --token\tNO\t\tDiscord user token ; if not specified, the script will search in DISCORD_TOKEN env\n\t\t\t\tOne of two must be defined (the script always take the parameter first)\n\t\t\t\tTo know how to get a user token, visit https://github.com/pbrissaud/discord-attachements-exporter/wiki/Usage-guide#grab-your-discord-token")
    print("-v, --verbose\tNO\t\tVerbose mode (more logs)")


if __name__ == "__main__":
    main(sys.argv[1:])
