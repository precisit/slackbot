import os
import time
import re
from slackclient import SlackClient


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
#EXAMPLE_COMMANDS = ["do", "wifi"]
COMMAND_DICT = {"wifi":"The password is... not available here yet.",
                "adress":"Klostergatan 9 \n 753 21 Uppsala",
                "help":"These are the available commands:\n",
                "love":"I love Precisit, not you.",
                "Hej":"Voff.",
                "Kerstin":"Kerstin gillar hundar och champagne. Hon exjobbar med recommender engines.",
                "Siri":"Siri gillar att sova och kan prata spanska. Hon jobbar som konsult.",
                "Simon":"Simon gillar att mingla och käka Paulúns frysmat. Simon jobbar som säljare.",
                "Sara":"Sara är fotbollsproffs (på riktigt) och gillar kaffe. Sara exjobbar med moln (inte regnmoln då).",
                "Marika":"Marika gillar att springa långt i skogen och att skriva texter. Hon jobbar som konsult.",
                "Martin":"Martin gillar geometri och hinderbanelöpning. Han jobbar med webbutveckling.",
                "Magnus":"Magnus gillar universum och gemenskap. Han jobbar med att förverkliga drömmar.",
                "Jonas":"Jonas gillar spel och spelutveckling. Han jobbar med spelutveckling.",
                "Jacob":"Jacob gillar tacos och hundar. Han jobbar med att skriva instruktioner för smarta stenar.",
                "Emma":"Jag känner inte Emma än men jag vet att hon är studentrepresentant och sociala medier-ansvarig.",
                "Karolin":"Jag känner inte Karolin än men jag vet att hon jobbar med marknadsföring.",
                "Precisit":"Precisit är världens bästa företag. :botil: :hearts: :precisit:.",
                "contribute":"If ya'll wanna contribute, you go do dat at https://github.com/precisit/slackbot."}
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    print(message_text)
    matches = re.search(MENTION_REGEX, message_text)
    print(matches)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try another command."

    # Finds and executes the given command, filling in response
    response = ""
    words = command.split(' ')

    if "help" in words:
        response =COMMAND_DICT["help"] + "\"" + "\"\n\"".join(COMMAND_DICT.keys()) + "\""
    else:
        for word in words:
            if word in COMMAND_DICT.keys():
                response = response + "\n" + COMMAND_DICT[word]

                if  response == "":
                    response = "I didn't understand"

    slack_client.api_call(        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
