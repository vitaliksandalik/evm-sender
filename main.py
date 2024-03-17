from decimal import Decimal

from web3 import Web3

from config import PRIVATE_KEY, AMOUNT_TO_SEND, TOKEN_CONTRACT_ADDRESS, load_selected_chain_config
from erc20_abi import erc20_abi
from utils import Logger

selected_chain_config = load_selected_chain_config()


class Sender:
    def __init__(self):
        self.logger = Logger('W3F', 'report.log')
        self.currency_symbol = selected_chain_config['symbol']
        self.chain_id = selected_chain_config['chainId']
        self.rpc_url = selected_chain_config['rpcUrl']
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
        self.nonce = self.w3.eth.get_transaction_count(self.account.address, 'pending')
        self.remaining_balance = self.w3.eth.get_balance(self.account.address)
        self.load_addresses()

    def load_addresses(self):
        try:
            with open('addresses.txt', 'r') as file:
                self.addresses = [address.strip() for address in file if address.strip()]
        except FileNotFoundError:
            self.logger.error("Addresses file not found.")
            raise

    def send_native_currency(self, address, amount):
        try:
            value = self.w3.to_wei(Decimal(amount), 'ether')
            gas_price = self.w3.eth.gas_price
            estimated_gas = self.w3.eth.estimate_gas({'from': self.account.address, 'to': address, 'value': value})
            total_cost = value + (estimated_gas * gas_price)

            if self.remaining_balance < total_cost:
                self.logger.error(f"Insufficient funds for transaction to {address}. Transaction aborted.")
                return

            tx = {
                    'nonce': self.nonce,
                    'to': address,
                    'value': value,
                    'gasPrice': gas_price,
                    'gas': estimated_gas,
                    'chainId': self.chain_id,
                }
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 1:
                self.nonce += 1
                self.remaining_balance -= total_cost
                self.logger.info(f"Transaction success: {amount} {self.currency_symbol} sent to {address} | Tx Hash: {tx_hash.hex()}")
                self.logger.info(f"Remaining Balance: {self.w3.from_wei(self.remaining_balance, 'ether')} {self.currency_symbol}")
            else:
                self.logger.error(f"Transaction to {address} failed. Tx Hash: {tx_hash.hex()}")
        except Exception as e:
            self.logger.error(f"Error during transaction to {address}: {e}")

    def send_token_transaction(self, address, amount, token_contract_address):
        try:
            contract = self.w3.eth.contract(address=token_contract_address, abi=erc20_abi)
            decimals = contract.functions.decimals().call()
            token_symbol = contract.functions.symbol().call()
            token_amount = int(Decimal(amount) * (10 ** decimals))
            gas_price = self.w3.eth.gas_price
            
            tx_dict = {
                'from': self.account.address,
                'to': token_contract_address,
                'data': contract.encodeABI(fn_name='transfer', args=[address, token_amount]),
                'value': 0,
                'gasPrice': gas_price,
                'nonce': self.nonce,
                'chainId': self.chain_id
            }

            estimated_gas = self.w3.eth.estimate_gas(tx_dict)
            tx_dict['gas'] = estimated_gas

            if self.w3.eth.get_balance(self.account.address) < estimated_gas * gas_price:
                self.logger.error("Insufficient ETH for gas. Transaction aborted.")
                return
            
            
            signed_tx = self.w3.eth.account.sign_transaction(tx_dict, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                self.nonce += 1
                token_balance = contract.functions.balanceOf(self.account.address).call()
                self.remaining_balance -= estimated_gas
                self.logger.info(f"Token transfer success: {amount} {token_symbol} sent to {address} | Tx Hash: {tx_hash.hex()}")
                self.logger.info(f"Remaining Balance: {token_balance / (10 ** decimals)} {token_symbol} | {self.w3.from_wei(self.remaining_balance, 'ether')} {self.currency_symbol}")
            else:
                self.logger.error(f"Transaction to {address} failed. Tx Hash: {tx_hash.hex()}")
        except Exception as e:
            self.logger.error(f"Error during token transaction to {address}: {e}")



def main():
    sender = Sender()
    if TOKEN_CONTRACT_ADDRESS:
        for address in sender.addresses:
            sender.send_token_transaction(address, AMOUNT_TO_SEND, TOKEN_CONTRACT_ADDRESS)
    else:
        for address in sender.addresses:
            sender.send_native_currency(address, AMOUNT_TO_SEND)


if __name__ == "__main__":
    main()
