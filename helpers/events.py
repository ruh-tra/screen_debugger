import win32evtlog
from time import sleep

class Event():
    def __init__(
            self, id, provider, time = None, type = None,
            level = None, message = None, xml = None, channel = None
            ):
        self.time = time
        self.id = id
        self.type = type
        self.level = level
        self.message = message
        self.process = provider
        self.xml = xml
        self.channel = channel
        self.unique_files = 0
        self.occurances = 0

    def get_attributes(self):
        return (
            self.time,
            self.id,
            self.type,
            self.level,
            self.message,
            self.process,
            self.xml,
            self.channel
        )
    
    def __eq__(self, other):
        if self.id == other.id and self.process == other.process:
            return True
        return False
    
    def __hash__(self):
        return hash((self.id, self.process))

def get_events(time):
    sleep(60)
    channels = win32evtlog.EvtOpenChannelEnum(None, 0)
    selected_events = []

    type_mapping = {
        0 : 'Audit Success',
        1 : 'Critical',
        2 : 'Error',
        3 : 'Warning',
        4 : 'Information',
        5 : 'Verbose'
    }

    while True:
        try:
            channel = win32evtlog.EvtNextChannelPath(channels)

            if channel:
                handle = win32evtlog.EvtQuery(
                    channel, win32evtlog.EvtQueryChannelPath, '*'
                )
                
                while True:
                    events = win32evtlog.EvtNext(handle, 1)
                    context = win32evtlog.EvtCreateRenderContext(win32evtlog.EvtRenderContextSystem)
                    if not events:
                        break
                    for event in events:
                        result = win32evtlog.EvtRender(
                            event, win32evtlog.EvtRenderEventValues, Context = context
                        )

                        event_time, _ = result[win32evtlog.EvtSystemTimeCreated]
                        time_difference = time - event_time
                        if time_difference.total_seconds() >= 120:
                            continue
                        readable_td = str(event_time)[0:-13].replace(':', '-').replace(' ', '_')
                        provider, _ = result[win32evtlog.EvtSystemProviderName]
                        event_id, _ = result[win32evtlog.EvtSystemEventID]
                        level, _ = result[win32evtlog.EvtSystemLevel]
                        xml = win32evtlog.EvtRender(event, win32evtlog.EvtRenderEventXml)
                            
                        metadata = win32evtlog.EvtOpenPublisherMetadata(provider)
                        message = win32evtlog.EvtFormatMessage(
                            metadata, event, win32evtlog.EvtFormatMessageEvent
                        )

                        selected_events.append(
                        Event(
                                channel = channel,
                                id = event_id,
                                level = level,
                                message = message,
                                provider = provider,
                                time = readable_td,
                                type = type_mapping[level], 
                                xml = xml,
                            )
                        )
            else:
                break

        except:
            return selected_events