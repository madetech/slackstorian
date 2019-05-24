import json
import slacker


class AuthenticationError(Exception):
    pass


class Channels(object):
    def __init__(self, channels_array):
        self.list = channels_array

    def as_json(self) -> str:
        return to_json(self.list)


def to_json(data) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


class SlackClient(object):
    """Wrapper around the Slack API.  This provides a few convenience
    wrappers around slacker.Slacker for the particular purpose of history
    download.
    """

    def __init__(self, token):
        self.slack = slacker.Slacker(token=token)  # todo set retry limit here

        # Check the token is valid
        try:
            self.slack.auth.test()
        except slacker.Error:
            raise AuthenticationError('Unable to authenticate API token.')

    def _get_history(self, channel_class, channel_id):
        """Returns the message history for a channel"""
        messages_array = []

        response = channel_class.history(
            channel=channel_id,
            latest=None,
            oldest=0,
            count=1000
        )

        messages_array = response.body['messages']

        while len(response.body['messages']) == 1000:

            oldest_timestamp = messages_array[-1]['ts']

            response = channel_class.history(
                channel=channel_id,
                inclusive=False,
                oldest=oldest_timestamp,
                count=1000
            )

            messages_array.extend(response.body['messages'])

        return messages_array

    def user_data_json(self):
        """Gets all user data as json"""
        data = self.slack.users.list().body['members']
        return to_json(data)

    def channels(self):
        """Returns a Channels object that contains a list of public channels."""
        return Channels(self.slack.channels.list().body['channels'])

    def channel_history(self, channel):
        """Returns the message history for a channel."""
        return to_json(self._get_history(self.slack.channels, channel_id=channel['id']))

    def post_to_channel(self, channel, message):
        return self.slack.chat.post_message(
            channel=channel, text=message, username="Slackstorian"
        )
