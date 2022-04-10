from builtins import str
from io import BytesIO

from ..client import Client
from ..communicators.tcp import TCPCommunicator
from ..formats.basic import BasicFormat
from ..serializers.json_serializer import JSONSerializer
from ..serializers.text_to_binary_serializer import TextToBinarySerializer


class JsonTCPClient(Client[bytes]):
    def __init__(self, host=u"localhost", port=2611):
        # type: (str, int) -> None
        super(JsonTCPClient, self).__init__(
            communicator=TCPCommunicator.connect(host=host, port=port),
            serializer=TextToBinarySerializer(JSONSerializer()),
            format_cls=BasicFormat,
            buffer_factory=BytesIO,
        )
