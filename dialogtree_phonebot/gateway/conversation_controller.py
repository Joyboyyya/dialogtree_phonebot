import asyncio 


class ConversationController():
    def __init__(self):
        self.participant_track = asyncio.Queue()
        self.outbound_track = asyncio.Queue()
        self.end_event = asyncio.Event()
        self.send_event = asyncio.Event()

    async def say(self, quote):
        await self.outbound_track.put(quote)

    async def ask(self,question):
        print('controller ask')
        await self.say(question)
        # print('question', question.get("question","Place holder"))
        self.send_event.set()
        retval = await self.participant_track.get()
        return retval

    def goodbye(self):
        self.end_event.set()
