
# coding: utf-8

# # My First Blockchain
#
# Contains code to create your own cryptocurrency. The name of the cryptocurrency created here is `hadcoin`
#
# Written with the help of Handelin de Ponteves and Kirill Eremenko.
#
# Check out their course [here](https://www.udemy.com/build-your-blockchain-az).
#
# ___
#
# ## Import Packages
#
# In order to build the cryptocurrency, we'll need to build upon what we wrote in "My-First-Blockchsin.ipynb". Hence, we will import it into this script. Hadelin does this by copy and pasting the previous work into the new script for the cryptocurrency, but importing it as I have here works as well.
#
# It also uses all of the packages that were inside the jupyter notebook.
#
# The script was created by downloading the relevant .ipynb as .py.

# In[4]:


# Import Blockchain class from BlockchainScript.py
from BlockchainScript import Blockchain

# Import additional packages.
import datetime
import hashlib
import json
import requests
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse


# ___
# ## Implement cryptocurrency

# In[5]:


class Cryptocurrency(Blockchain):

    # Update `__init__` to include transations
    def __init__(self):

        # Initialize chain and transactions
        self.chain = []
        self.transactions = []

        # Initialize Genesis Block
        self.create_block(proof = 1, previous_hash='0')

        # Initialize nodes
        self.nodes = set()


    def create_block(self, proof, previous_hash):
        """
        Creates a new block and appends it to the chain.

        proof: Proof of work,
        previous_hash: Hash of previous block, string.

        Returns a new block
        """
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block


    def add_transaction(self, sender, receiver, amount):
        """
        Add transaction to blockchain

        sender: Person sending money, string.
        receiver: Person receiving money, string.
        amount: Amount, the amount of money, int/float.

        Returns block index of new transaction.
        """
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1


    def add_node(self, address):
        """
        Add note to blockchain network.

        address: HTTP and Port of new node, string.
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


    def replace_chain(self):
        """
        Searches network for nodes that contain the longest valid chain and
        updates variables to reflect that.

        Returns True/False depending on if longer chain was found.
        """
        # Get network to search for longest chain
        network = self.nodes

        # Initialize `longest_chain` variable
        longest_chain = None

        # Get the current max length
        max_length = len(self.chain)

        # Search network for longer chains
        for nodes in network:

            # Get response from node
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # If longer valid chain is found then update that chain
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        # Implement update
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# ___
# ## Creating cryptocurrency webapp

# In[6]:


# Create instance of Cryptocurrency class
blockchain = Cryptocurrency()


# In[7]:


# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')


# In[ ]:


# Create web app
app = Flask(__name__)

# Create Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block(blockchain):
    """
    Mines a block for blockchain.

    Returns a response to client.
    """

    # Get details of previous block
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']

    # Find proof of the next block
    proof= blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver='Simon', amount=1)

    # Create new block
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
               'index': block['index'],
               'timestamp': block['timestamp'],
               'proof': block['proof'],
               'previous_hash': block['previous_hash'],
               'transactions': block['transactions']}

    return jsonify(response), 200


# Get Chain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    """
    Gets the current chain.

    Returns a response to client.
    """

    response = {'chain': blockchain.chain,
               'length': len(blockchain.chain)}

    return jsonify(response), 200


# Check Blockchain
@app.route('/is_valid', methods=['GET'])
def is_valid():
    """
    Checks if the current blockchain is valid.

    Returns a response to client.
    """

    # Get validity of blockchain
    is_valid = blockchain.is_chain_valid(blockchain.chain)

    if is_valid: response = {'message': 'The blockchain is valid!'}
    else: response = {'message': 'Error, the blockchain is invalid!'}

    return jsonify(response), 200


def main():
    app.run(host='0.0.0.0', port = 5000)


# Add new transactions
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """
    Add new transaction.
    """
    # Get json file
    json =  request.get_json()

    # Define transaction
    transaction_keys = ['sender', 'receiver', 'amount' ]

    # Check that transaction keys are valid
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400

    # Add transaction to blockchain
    index = blockchain.add_transaction(json['sender'],
                                       json['receiver'],
                                       json['amount'])

    # Create response
    response = {'message': f'This transaction will be added to Block {index}'}

    return jsonify(response), 201


# Decentralising the blockchain
@app.route('/connect_node', methods=['POST'])
def connect_node():
    """
    Connects nodes.
    """
    # Get json
    json =  request.get_json()

    # Get nodes
    nodes = json.get('nodes')

    # Check that nodes actually exist
    if nodes is None: return "No node", 400

    # Connect nodes
    for node in nodes: blockchain.add_node(node)
    response = {'message': "All the nodes are now connected. \n
                 The Hadcoin Blockchain now contains the following nodes:",
                'total_modes': list(blockchain.nodes)}

    return jsonify(response), 201


# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    """
    Checks if the current blockchain is valid.

    Returns a response to client.
    """

    # Get validity of blockchain
    is_chain_replaced = blockchain.replace_chain()

    if is_chain_replaced: response = {'message': 'Chain was replaced by longest one.',
                                      'new_chain': blockchain.chain}
    else: response = {'message': 'Current chain is up to date, no changes were made.',
                      'actual_chain': blockchain.chain}

    return jsonify(response), 200


def main():
    app.run(host='0.0.0.0', port = 5003)

# Running the app
if __name__ == "__main__":
    main()
else: main()
