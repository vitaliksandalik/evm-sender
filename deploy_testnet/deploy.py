import sys
import os
import time
from web3 import Web3
from solcx import compile_files, install_solc, get_installed_solc_versions
from solcx.exceptions import SolcNotInstalled

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from config import PRIVATE_KEY, load_selected_chain_config
from utils import Logger

# IMPORTANT: Ensure that you have selected a testnet RPC URL in config.py before proceeding.
# Note: This deploy.py script is designed to acquire some testnet ERC-20 tokens. Not all chains have token faucets.
# You should NOT use this for creating real tokens; I am not responsible for that. :D
selected_chain_config = load_selected_chain_config()


class Deployer:
    def __init__(self):
        self.logger = Logger('W3F', 'deployment.log')
        self.currency_symbol = selected_chain_config['symbol']
        self.chain_id = selected_chain_config['chainId']
        self.rpc_url = selected_chain_config['rpcUrl']
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
        self.abi, self.bytecode = self.compile_contract('Web3Forces.sol')

    def install_solc_version(self, version):
        try:
            if version not in get_installed_solc_versions():
                self.logger.info(f"solc version {version} not found. Installing...")
                install_solc(version)
                self.logger.info(f"Installed solc version {version}.")
            else:
                self.logger.info(f"solc version {version} is already installed.")
        except Exception as e:
            self.logger.error(f"Error installing solc version {version}: {e}")
            raise

    def compile_contract(self, contract_file, solc_version='0.8.24'):
        try:
            self.install_solc_version(solc_version)
            compiled_sol = compile_files([os.path.join(os.path.dirname(__file__), contract_file)],
                                         output_values=['abi', 'bin'], solc_version=solc_version)
            _, contract_interface = compiled_sol.popitem()
            bytecode = contract_interface['bin']
            abi = contract_interface['abi']
            self.logger.info(f"Contract {contract_file} compiled with solc {solc_version}.")
            return abi, bytecode
        except SolcNotInstalled as e:
            self.logger.error(f"Solc version {solc_version} is not installed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error compiling contract {contract_file}: {e}")
            raise

    def deploy_contract(self):
        try:
            self.logger.info("Starting contract deployment.")
            contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
            estimated_gas = contract.constructor().estimate_gas({'from': self.account.address})
            gas_price = self.w3.eth.gas_price
            total_cost = estimated_gas * gas_price

            account_balance = self.w3.eth.get_balance(self.account.address)
            if account_balance < total_cost:
                self.logger.error("Insufficient funds for gas. Deployment aborted.")
                return None

            constructor_txn = contract.constructor().build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': estimated_gas,
                'gasPrice': gas_price
            })

            signed_txn = self.w3.eth.account.sign_transaction(constructor_txn, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            self.logger.info(f"Contract deployed. Transaction hash: {tx_hash.hex()}")

            remaining_balance = account_balance - total_cost
            spent_amount_eth = self.w3.from_wei(total_cost, 'ether')
            remaining_balance_eth = self.w3.from_wei(remaining_balance, 'ether')

            self.logger.info(f"Spent: {spent_amount_eth} {self.currency_symbol} | Remaining Balance: {remaining_balance_eth} {self.currency_symbol}")

            self.wait_for_blocks(1)
            return tx_receipt.contractAddress
        except Exception as e:
            self.logger.error(f"Error during contract deployment: {e}")
            return None

    def wait_for_blocks(self, n):
        start_block = self.w3.eth.block_number
        target_block = start_block + n
        while self.w3.eth.block_number < target_block:
            time.sleep(3)
        self.logger.info(f"Waited for {n} block(s).")

    def log_contract_info(self, contract_address):
        try:
            contract = self.w3.eth.contract(address=contract_address, abi=self.abi)

            symbol = contract.functions.symbol().call()
            name = contract.functions.name().call()
            total_supply = contract.functions.totalSupply().call()
            total_supply_converted = self.w3.from_wei(total_supply, 'ether')

            self.logger.info(f"Contract address: {contract_address}") 
            self.logger.info(f"Contract Name: {name}")
            self.logger.info(f"Ticker (Symbol): {symbol}")
            self.logger.info(f"Total Supply: {total_supply_converted} {symbol}")
        except Exception as e:
            self.logger.error(f"Error retrieving contract information for {contract_address}: {e}")

def main():
    deployer = Deployer()
    try:
        contract_address = deployer.deploy_contract()
        deployer.log_contract_info(contract_address)
    except Exception as e:
        deployer.logger.error(f"Deployment failed: {e}")

if __name__ == "__main__":
    main()