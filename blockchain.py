import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Creating First BLock
        self.new_block(previous_hash='1', proof=100,secret_key='firstonerandomsecretkey')

    #registering neighbouring nodes
    def register_node(self, address):

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def valid_chain(self, chain):
       

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof'], last_block['previous_hash']):
                print("Not valid chain")
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
    

        neighbours = self.nodes
        new_chain = None
        window_size=10

        max_length = len(self.chain)
        print(max_length)
        #Calculating HWD of Each neighboours
        for node in neighbours:
            print(node)
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                print("max length  :"+str(max_length))
                print("length  :"+str(length))
                chain = response.json()['chain']
                sameupto=0
                rate=dict()
                n_rate=dict()
                window=10
                HWD=0
                diff=0
                n_HWD=0
                n_diff=0
                window_start=max_length-window
                neigh_window_start=length-window
                n_rate['firstonerandomsecretkey']=0
                rate['firstonerandomsecretkey']=0
                if(window_start<0):
                    window_start=0
                if(neigh_window_start<0):
                    neigh_window_start=0
                for i in range(0,min(max_length,length)):
                    try:
                        if(chain[i]==self.chain[i]):
                            print("same over here "+str(i))
                            sameupto=i
                    except:
                        print(str(node)+"  :"+str(i))
                for i in range(window_start,max_length):
                    try:
                        rate[self.chain[i]['secret_key']]+=1
                    except:
                        rate[self.chain[i]['secret_key']]=1
                for i in range(neigh_window_start,length):
                    try:
                        n_rate[chain[i]['secret_key']]+=1
                    except:
                        n_rate[chain[i]['secret_key']]=1
                for i in range(sameupto,max_length):
                    diff=diff+self.chain[i]['difficulty']
                for i in range(sameupto,length):
                    n_diff=n_diff+chain[i]['difficulty']
                for i in range(sameupto,max_length):
                    HWD=(rate[self.chain[i]['secret_key']]/window)*diff
                for i in range(sameupto,length):
                    n_HWD=(n_rate[chain[i]['secret_key']]/window)*n_diff
                print(HWD)
                print(n_HWD)
                
                
                    
                # Check if the HWD larger
                if(n_HWD > HWD):
                    print("hahahahahahahaha")
                    new_chain = chain

        # Replace our chain if we discovered a new greated HWD one
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash,secret_key):
       

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'secret_key': secret_key,
            'difficulty': 1
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):

       
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"



app = Flask(__name__)


node_identifier = str(uuid4()).replace('-', '')


blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    values = request.get_json()
    print(values)
    
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)
    secret_key=values['secret_key']
    
    # Adding reward.
    
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash,secret_key)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        #adding secret key of miner along with block for our block chain
        'secret_key' : secret_key,
        'difficulty' : block["difficulty"]
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)