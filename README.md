# Discord Attachements Exporter

DiscordAttachementsExporter can be used to export attachements (files, pictures, videos) from Discord channels specified in a file. It uses [Tyrrrz/DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) to export message history from a Discord channel. A big thanks to him !

# Requirements

The script needs Python (version > 3.5), pip and Docker to run.

:heavy_check_mark: Tested on Ubuntu 20.04 LTS with Python 3.8.5 , Pip 20.3.1 and Docker 19.03.13

The script should be runnable on all OS (tests incoming)

# Installation

Install pip packages and pull Tyrrrz/DiscordChatExporter image container :

```
cd discord-attachements-exporter
pip3 install -r requirements.txt
docker pull "tyrrrz/discordchatexporter:stable
```

# Usage

```
python3 main.py [OPTIONS]

OPTION          REQUIRED        DESCRIPTION
-h, --help      NO              Show manual
-i, --input     YES             Path to config file
-o, --output    NO              Path to directory where attachements will be downloaded
-t, --token     NO              Discord user token (if not defined, the DISCORD_TOKEN env must be)
-v, --verbose   NO              Verbose mode
```

# Example

```
python3 main.py -i channels_list -o /path/to/folder -t DISCORD_TOKEN
```

Once the script finished the attachements will be under /path/to/folder/ with the following structure :

```
/path/to/folder/
├── channel1_name
|   ├── attachement1
|   ├── attachement2
|   ...
├── channel2_name
|   ├── attachement1
|   ├── attachement2
|   ...
...
```

# Read the doc !

To know to create the config file and get your Discord User Token and to get more examples, check out the [wiki](https://github.com/pbrissaud/discord-attachements-exporter/wiki) !
