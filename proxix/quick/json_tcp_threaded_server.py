from builtins import str
from io import BytesIO

from ..formats.basic import BasicFormat
from ..listeners.tcp import TCPListener
from ..serializers.json_serializer import JSONSerializer
from ..serializers.text_to_binary_serializer import TextToBinarySerializer
from ..servers.threaded import ThreadedServer


class JsonTCPThreadedServer(ThreadedServer[bytes]):
    def __init__(self, host=u"0.0.0.0", port=2611):
        # type: (str, int) -> None
        super(JsonTCPThreadedServer, self).__init__(
            listener=TCPListener.create(host, port),
            serializer=TextToBinarySerializer(JSONSerializer()),
            format_cls=BasicFormat,
            buffer_factory=BytesIO,
        )
