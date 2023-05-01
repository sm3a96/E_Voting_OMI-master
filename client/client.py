import socket
import time

from utils.Message_Type import MESSAGE
from utils.messages.voter_messages import Voter_Registration_Message, Voter_Heartbeat_Message

class Client:
    def __init__(self, id, logger):
        # self.voting_vector = {
        #     "What is the best CS class?": ["240", "555", "511"],
        #     "What is the hardest homework in CSCI 55500?": ["H1", "H2", "H3"],
        #     "Who is the best professor in the CS department?": ["Xzou", "Kelly", "Andy"]
        # } 
        self.server = socket.gethostbyname('localhost')
        self.header = 64
        self.format = 'utf-8'
        self.length = 1000
        self.id = id
        self.logger = logger
        self.location = 0
        self.location_tracker = 0
    
    def start_channel_with_admin(self, port):
        self.admin_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.admin_sock.connect((self.server, int(port)))

    def start_channel_with_collector1(self, port):
        self.c1_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.c1_sock.connect((self.server, int(port)))

    def start_channel_with_collector2(self, port):
        self.c2_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.c2_sock.connect((self.server, int(port)))

    def send_message(self, message, sock):
        time.sleep(0.1)
        sock.sendall(message)

    def receive_message(self, sock):
        timeout = 10
        message = None
        sock.settimeout(timeout)
        try:
            message = sock.recv(int(self.length))
            while message == b'':
                message = sock.recv(int(self.length))
        except:
            self.logger.debug(f'No message received within {timeout} seconds, continuing to listen...')
            voter_heartbeat_message = Voter_Heartbeat_Message()
            self.send_message(voter_heartbeat_message.to_bytes(), sock)
            self.receive_message(sock)
        if message:
            message_type = int.from_bytes(message.split(b',')[0], byteorder='big')
            # receive collectors information from the admin
            if message_type == MESSAGE.METADATA_VOTER.value:
                self.logger.info(f'Received collectors information.\nclosing connection with admin')
                self.close_connection(self.admin_sock)
                self.extract_collectors_information(message)
                self.connect_with_collector2(message)
                self.receive_message(self.c2_sock)
                self.close_connection(self.c2_sock)
                self.connect_with_collector1(message)
                self.receive_message(self.c1_sock)
                self.close_connection(self.c1_sock)
            if message_type == MESSAGE.VOTER_LOCATION.value:
                self.logger.debug(f'Received location from collector: {message}')
                self.extract_location(message)  
                self.location_tracker += 1
                if self.location_tracker == 2:
                    self.logger.info(f'Location: {self.location}')
        else:
            return

    def close_connection(self, sock):
        disconnect_message = MESSAGE.DISCONNECT.value.to_bytes(1, byteorder='big')
        self.send_message(disconnect_message, sock)
        time.sleep(0.1)
        sock.close()
        self.logger.info('Connection closed successfully.')
    
    def extract_collectors_information(self, message):
        message_parts = message.split(b',')
        self.election_id = message_parts[1].decode()
        self.c1_host = message_parts[3].decode()
        self.c1_port = int.from_bytes(message_parts[4], byteorder='big')
        self.c1_pk_length = message_parts[5].decode()
        self.c1_pk= message_parts[6].decode()
        self.c2_host = message_parts[8].decode()
        self.c2_port = int.from_bytes(message_parts[9], byteorder='big')
        self.c2_pk_length = message_parts[10].decode()
        self.c2_pk = message_parts[11].decode()
        self.m = message_parts[12].decode()

    def extract_location(self, message):
        message_parts = message.split(b',')
        self.location += int.from_bytes(message_parts[2], byteorder='big')

    def connect_with_collector2(self, message):
        self.logger.info(f'Establishing a connection with collector 2 and sending it a registration request')
        self.start_channel_with_collector2(self.c2_port)
        message = Voter_Registration_Message(self.id)
        self.send_message(message.to_bytes(), self.c2_sock)

    def connect_with_collector1(self, message):
        self.logger.info(f'Establishing a connection with collector 1 and sending it a registration request')
        self.start_channel_with_collector1(self.c1_port)
        message = Voter_Registration_Message(self.id)
        self.send_message(message.to_bytes(), self.c1_sock)

    def start_voting(self):
        self.logger.info(list(self.voting_vector.keys())[0])
        self.logger.info(list(self.voting_vector.values())[0])
        q1_answer = input("")
        if q1_answer not in list(self.voting_vector.values())[0]:
            raise Exception("Answer is not in the list")
        self.logger.info(list(self.voting_vector.keys())[1])
        self.logger.info(list(self.voting_vector.values())[1])
        q2_answer = input("")
        if q2_answer not in list(self.voting_vector.values())[1]:
            raise Exception("Answer is not in the list")
        self.logger.info(list(self.voting_vector.keys())[2])
        self.logger.info(list(self.voting_vector.values())[2])
        q3_answer = input("")
        if q3_answer not in list(self.voting_vector.values())[2]:
            raise Exception("Answer is not in the list")
        return q1_answer + "," + q2_answer + "," + q3_answer
    
    def generate_voting_vector(self, vote):
        vector = '000000000'
        voting_list = []
        for i in range(len(list(self.voting_vector.keys()))):
            q_vote = vote.split(',')[i]
            q = list(self.voting_vector.values())[i]
            answer_index = q.index(q_vote) + (3 * self.location)
            vector_list = list(vector)
            vector_list[answer_index] = '1'
            new_vector = ''.join(vector_list)
            v = int(new_vector, 2)
            v_prime = int(new_vector[::-1], 2)
            voting_list.append([v, v_prime]) 
        return voting_list
    
    def generate_all_ballots(self, vote, shares):
        ballots = self.generate_ballots(vote[0], shares[0])
        ballots_prime = self.generate_ballots(vote[1], shares[1])
        return [ballots, ballots_prime]

    def generate_ballots(self, vote, shares):
        return vote + sum(shares)
    
    # def get_shares(self):
    #     share = 0
    #     share_prime = 0
    #     self.send_message('give me shares')
    #     message_from_server = self.sock.recv(self.header).decode(self.format)
    #     share = int(message_from_server.split(',')[0])
    #     share_prime = int(message_from_server.split(',')[1])
    #     return [share, share_prime]