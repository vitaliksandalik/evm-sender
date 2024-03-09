import os
import json
from dotenv import load_dotenv

load_dotenv()

SUPPORTED_CHAINS = [
    "Ethereum Mainnet", "Ethereum Sepolia",
    "BSC Mainnet", "BSC Testnet",
    "Polygon Mainnet", "Polygon Mumbai",
    "Avalanche C-Chain", "Avalanche Fuji Testnet",
    "Fantom Mainnet", "Fantom Testnet",
    "Base Mainnet", "Base Sepolia",
    "Arbitrum One", "Arbitrum Sepolia",
    "OP Mainnet", "Optimism Sepolia",
    "Blast Mainnet", "Blast Sepolia",
]

# Select blockchain network to use
SELECTED_CHAIN = "Ethereum Sepolia"

PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Amount of currency to send in transactions
AMOUNT_TO_SEND = "0.01"

# Contract address for the token to be sent. Leave empty if sending the blockchain's native currency.
TOKEN_CONTRACT_ADDRESS = ""


def load_selected_chain_config():

    with open("chains.json", "r") as file:
        chains_config = json.load(file)

    selected_chain_config = next(
        (chain for chain in chains_config if chain["name"].strip().lower() == SELECTED_CHAIN.strip().lower()),
        None,
    )

    if selected_chain_config is None:
        raise ValueError("Selected chain configuration not found. Please check your config.")

    return selected_chain_config
