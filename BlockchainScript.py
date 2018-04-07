
# coding: utf-8

# # My First Blockchain
# 
# Written with the help of Handelin de Ponteves and Kirill Eremenko.
# 
# Check out their course [here](https://www.udemy.com/build-your-blockchain-az).
# 
# **Notes**
# 
# Requires `Flask v 0.12.2`
# 
# Postman HTTP Client: `https://www.getpostman.com`
# 
# ___
# ## Import Packages

# In[1]:


import datetime
import hashlib
import json
from flask import Flask, jsonify


# ___
# ## Building the Blockchain

# In[2]:


# Create Blockchain Class
class Blockchain:
    
    def __init__(self):
        # Initialize Chain
        self.chain = []
        
        # Initialize Genesis Block
        self.create_block(proof = 1, previous_hash = '0')
     
    
    def create_block(self, proof, previous_hash):
        """
        Creates a new block and appends it to the chain.
        
        proof: Proof of work, 
        previous_hash: Hash of previous block, string. 
        
        Returns a new block
        """
        # Define the block based on input parameters
        block = {'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'previous_hash': previous_hash} # Also possible to add a further 'data field
        
        # Append Block to Chain
        self.chain.append(block)
        
        return block
    
    
    def get_previous_block(self):
        """
        Returns the previous block in a blockchain.
        """
        # Return previous block
        
        return self.chain[-1]
    
    
    def proof_of_work(self, previous_proof):
        """
        Creates proof_of_work for new block.
        
        previous_proof: Previous nonce, int.
        
        Returns nonce of new_proof
        """
        
        # Init. new_proof and check_proof variables
        new_proof = 1
        check_proof = False
        
        # Find a proof of work that solves problem
        while check_proof is False:
            
            hash_operation = hashlib.sha256(
                str(
                    new_proof**2 - previous_proof**2).encode()).hexdigest()
            # hash_operation is required to have four leading zeros, can be changed.
            if hash_operation[:4] == '0000': check_proof = True
            else: new_proof+=1 # Try again with new proof
                
        return new_proof
            
        
    def hash(self, block):
        """
        Returns hash for corresponding block by using its dictionary defined in 
        `create_block()`.
        
        block: Block in chain, block.
        
        Returns hash of block
        """
        # Find the hash for the block
        encoded_block = json.dumps(block, sort_keys = True).encode()
        
        return hashlib.sha256(encoded_block).hexdigest()
    
    
    def is_chain_valid(self, chain):
        """
        Checks if chain is valid.
        
        chain: Blockchain, chain
        """
        
        # Init. variables for while loop
        previous_block = chain[0]
        block_index = 1
        
        # Check that each block in the chain is valid
        while block_index < len(chain):
            # Get corresponding block
            block = chain[block_index]
            
            # Check previous_hash
            if block['previous_hash'] != self.hash(previous_block): return False
            
            # Check proof
            # Get proofs
            previous_proof = previous_block['proof']
            proof = block['proof']
            
            # Find hash
            hash_operation = hashlib.sha256(
                str(
                    proof**2 - previous_proof**2).encode()).hexdigest()
            
            # Invalidate if leading values are not '0000'
            if hash_operation[:4] != '0000': return False
            
            # Move along chain if everything is okay
            previous_block=block
            block_index+=1
            
        return True


# ___
# ## Mining the Blockchain

# In[3]:


# Create web app
app = Flask(__name__)

# Create Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    """
    Mines a block.
    
    Returns a response to client.    
    """
    
    # Get details of previous block
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    
    # Find proof of the next block
    proof= blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    # Create new block
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
               'index': block['index'],
               'timestamp': block['timestamp'],
               'proof': block['proof'],
               'previous_hash': block['previous_hash']}
    
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

# Running the app
if __name__ == "__main__":
    main()
else: pass

