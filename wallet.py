# %%
# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
import os
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware

# %%

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")


# %%

# Import constants.py and necessary functions from bit and web3
# YOUR CODE HERE
from constants import *
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
 
 


# %%
# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    
    command = f'php ./hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --numderive="{numderive}" --coin="{coin}" --format=json' 
    
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
   
    keys = json.loads(output)
    return  keys


# %%
# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {"eth", "btc-test", "btc"}
numderive = 3
keys = {}
for coin in coins:
    keys[coin]= derive_wallets(mnemonic, coin, numderive=3)



# %%
eth_PrivateKey = keys["eth"][0]['privkey']
btc_PrivateKey = keys['btc-test'][0]['privkey']


# %%
# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin,priv_key):
    print(coin)
    print(priv_key)
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)



# %%
print(json.dumps(eth_PrivateKey, indent=4, sort_keys=True))
print(json.dumps(btc_PrivateKey, indent=4, sort_keys=True))




# %%
print(json.dumps(keys, indent=4, sort_keys=True))

# %%
# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin,account, recipient, amount):
    if coin == ETH: 
        gasEstimate = w3.eth.estimateGas(
            {"from":eth_acc.address, "to":recipient, "value": amount}
        )
        return { 
            "from": eth_acc.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(eth_acc.address)
        }
    
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])



# %%
# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin,account,recipient, amount):
    txn = create_tx(coin, account, recipient, amount)
    if coin == ETH:
        signed_txn = eth_acc.sign_transaction(txn)
        result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(result.hex())
        return result.hex()
    elif coin == BTCTEST:
        tx_btctest = create_tx(coin, account, recipient, amount)
        signed_txn = account.sign_transaction(txn)
        print(signed_txn)
        return NetworkAPI.broadcast_tx_testnet(signed_txn)