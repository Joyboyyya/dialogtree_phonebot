To run this openai, fastapi, aiofiles, and starlette must be installed in its local environment
Run 
python -m dialogtree_phonebot.gateway.app 
from the top level directory of this project to start it
The call's script must be located at
./dialogtree_phonebot/dialogtree/example.xml


Each individual conversation needs a call_sid to identify it. Once a conversationr reaches its end, the chatbot will stop responding to further attempts to converse and you
will need to start a new one

example interaction:

In [17]: requests.post('http://localhost:8080/make-call', json={'call_sid':'a'}).json()
Out[17]: '\nHi! I am your pet purchasing assistant.\nAre you interested in purchasing a cat or a dog?\n'

In [18]: requests.post('http://localhost:8080/converse', json={'call_sid':'a', 'quote':'I would like a cat'}).json()
Out[18]: '\nYou have selected cats.\n\n\nAre you allergic to cats?\n'

In [19]: requests.post('http://localhost:8080/converse', json={'call_sid':'a', 'quote':'I am'}).json()
Out[19]: '\nDo you have space for your cat to roam?\n'

In [20]: requests.post('http://localhost:8080/converse', json={'call_sid':'a', 'quote':'I have outdoor space'}).json()
Out[20]: '\nDo you like your questions direct or do you prefer to beat around the bush?\n'

In [21]: requests.post('http://localhost:8080/converse', json={'call_sid':'a', 'quote':'I like direct questions'}).json()
Out[21]: 'Siberian cat\n\nThanks for talking to me. Goodbye.\n'

