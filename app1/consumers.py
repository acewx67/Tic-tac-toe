from channels.consumer import SyncConsumer,AsyncConsumer
from channels.exceptions import StopConsumer
import uuid
import json
from asgiref.sync import async_to_sync
from . models import Array
import queue
import random
import time
class MySyncConsumer(SyncConsumer):
    conns = queue.Queue()
    groups = {}
    def websocket_connect(self,event):
        # class to handle the different clients connecting to our server
        MySyncConsumer.conns.put(self)
        # Generate a unique identifier for the connection
        self.send({
            'type': 'websocket.accept',
        })
        while MySyncConsumer.conns.qsize() >=2 :
            i = 0
            uid = str(uuid.uuid4())
            x,y = 0,0
            for i in range(2):
                conn = MySyncConsumer.conns.get()
                if x == 0:
                    x = conn
                    MySyncConsumer.groups[uid] = {x : 0}
                elif y == 0:
                    MySyncConsumer.groups[uid][x] = conn
                    x = 0
                conn.group_name = uid
                async_to_sync(conn.channel_layer.group_add)(uid,conn.channel_name)
            else:
                print(MySyncConsumer.groups)
                text_data = json.dumps({'enoughPlayers' : True})
                async_to_sync(list(MySyncConsumer.groups.get(uid,None).keys())[0].channel_layer.group_send)(uid,{
                    'type':'chat.msg',
                    'text':text_data,
                })
                array = Array(group_name = uid)
                array.save()
                # sending group name to both websocket endpoints
                text_data = json.dumps(uid)
                async_to_sync(list(MySyncConsumer.groups.get(uid,None).keys())[0].channel_layer.group_send)(uid,{
                    'type':'chat.msg',
                    'text':text_data,
                })
                #randomly choose one player to begin the match
                # Randomly choose between 0 and 1, one group object has only
                random_player_index = random.randint(0, 1)
                if random_player_index :
                    print('in blockksss')
                    list(MySyncConsumer.groups.get(uid,None).keys())[0].send({
                        'type' : 'websocket.send',
                        'text' : json.dumps({
                            'playerTurn' : True,
                            'playerInput' : 'x'
                        })
                    })
                    list(MySyncConsumer.groups.get(uid,None).keys())[0].playerInput = 'x'
                    MySyncConsumer.groups.get(uid,None)['player_X'] = list(MySyncConsumer.groups.get(uid,None).keys())[0]
                    
                    MySyncConsumer.groups.get(uid,None).get(list(MySyncConsumer.groups.get(uid,None).keys())[0],None).send({
                        'type' : 'websocket.send',
                        'text' : json.dumps({
                            'playerTurn' : False,
                            'playerInput' : 'o'
                        })
                    })
                    MySyncConsumer.groups.get(uid,None).get(list(MySyncConsumer.groups.get(uid,None).keys())[0],None).playerInput = 'o'
                    MySyncConsumer.groups.get(uid,None)['player_O'] = MySyncConsumer.groups.get(uid,None).get(list(MySyncConsumer.groups.get(uid,None).keys())[0],None)
                else:
                    MySyncConsumer.groups.get(uid,None).get(list(MySyncConsumer.groups.get(uid,None).keys())[0],None).send({
                        'type' : 'websocket.send',
                        'text' : json.dumps({
                            'playerTurn' : True,
                            'playerInput' : 'x'
                        })
                    })
                    MySyncConsumer.groups.get(uid,None).get(list(MySyncConsumer.groups.get(uid,None).keys())[0],None).playerInput = 'x'
                    MySyncConsumer.groups.get(uid,None)['player_X'] = MySyncConsumer.groups.get(uid,None).get(list(MySyncConsumer.groups.get(uid,None).keys())[0],None)
                    
                    list(MySyncConsumer.groups.get(uid,None).keys())[0].send({
                        'type' : 'websocket.send',
                        'text' : json.dumps({
                            'playerTurn' : False,
                            'playerInput' : 'o'
                        })
                    })
                    list(MySyncConsumer.groups.get(uid,None).keys())[0].playerInput = 'o'
                    MySyncConsumer.groups.get(uid,None)['player_O'] = list(MySyncConsumer.groups.get(uid,None).keys())[0]


                
        if MySyncConsumer.conns.qsize() <= 1:
            self.send({
                "type": "websocket.send",
                "text": json.dumps({
                    'enoughPlayers': False
                })
            })

        print('websocket connection established')

    def chat_msg(self,event):
        print('in fucn')
        print('msg....',event)
        self.send({
            'type':'websocket.send',
            'text': event['text']
        })
    
    def calc_winner(self,array):
        print(array)
        indices = [
            [0,1,2],
            [3,4,5],
            [6,7,8],
            [0,3,6],
            [1,4,7],
            [2,5,8],
            [0,4,8],
            [2,4,6]
        ]

        print('len od indices',len(indices))

        for i in range(len(indices)):
            if array[indices[i][0]]:
                print('jopl')
                if array[indices[i][0]] == array[indices[i][1]] and array[indices[i][0]] == array[indices[i][2]]:
                    print('aziluyj')
                    return array[indices[i][0]]
        if not None in array:
            return "draw"
        return None



    
    def websocket_receive(self,event):
        player = json.loads(event.get('text'))['player']
        group = json.loads(event.get('text'))['group_name']
        update_index = json.loads(event.get('text'))['update_index']
        # print(MySyncConsumer.groups)
        # print(MySyncConsumer.groups.get(group))
        # print(group)
        print('///////////')
        # print(MySyncConsumer.groups[group].get('player_X'))
        time.sleep(0.5)
        instance = Array.objects.get(pk=group)
        array = instance.data
        print('this is dataaaaaaaaaaa',array)
        winner = self.calc_winner(array)
        print('(((((((((((((((((())))))))))))))))))')
        print(winner)
        if winner == "draw":
            async_to_sync(list(MySyncConsumer.groups.get(group,None).keys())[0].channel_layer.group_send)(group,{
                    'type':'chat.msg',
                    'text': json.dumps({
                        'winner_player' : 'draw', 
                    })
                })
        elif winner is not None :
            if winner == 'x':
                async_to_sync(list(MySyncConsumer.groups.get(group,None).keys())[0].channel_layer.group_send)(group,{
                    'type':'chat.msg',
                    'text': json.dumps({
                        'winner_player' : 'x', 
                    })
                })
            else:
                async_to_sync(list(MySyncConsumer.groups.get(group,None).keys())[0].channel_layer.group_send)(group,{
                    'type':'chat.msg',
                    'text': json.dumps({
                        'winner_player' : 'o',
                    })
                })
            instance.delete()
        elif player == 'x':
            MySyncConsumer.groups[group].get('player_O').send({
                'type' : 'websocket.send',
                'text' : json.dumps({
                    'playerTurn' : True,
                    'update_index' : update_index
                })
            })
        else:
            MySyncConsumer.groups[group].get('player_X').send({
                'type' : 'websocket.send',
                'text' : json.dumps({
                    'playerTurn' : True,
                    'update_index' : update_index
                })
            })
    
    def websocket_disconnect(self,event):
        text_data = f"{self} player has disconnected..."
        async_to_sync(self.channel_layer.group_send)(self.group_name,{
            'type':'chat.msg',
            'text':text_data,
        })
        array = Array.objects.filter(group_name=self.group_name)
        print(array)
        array.delete()
        print(f'data deleted for {self,self.group_name}')
        print('websocket disconnected..',event)
        raise StopConsumer()

    







































class MyAsyncConsumer(AsyncConsumer):
    async def websocket_connect(self,event):
        print('websocket connection established',event)
        await self.send({
            'type': 'websocket.accept'
        })
        await self.send({
            'type':'websocket.send',
            'text':'connection established'
        })
    
    async def websocket_receive(self,event):
        print('Message received..',event)
        await self.send({
            'type':'websocket.send',
            'text':'msg received'
        })
    
    async def websocket_disconnect(self,event):
        print('websocket disconnected..')
        raise StopConsumer()