# **EVM Compatible Chains Transaction Sender Guide**

**Welcome** to the EVM Transaction Sender guide! This document will help you set up and run a Python script to send transactions from one wallet to many wallets. The instructions are designed for users with no prior programming or blockchain experience. Follow the steps closely to ensure a smooth setup on both Windows and Mac operating systems.

## **Prerequisites**

Before starting, make sure you have the following:

- **Python 3.8 or later**: If you don't have Python installed, download it from [python.org](https://python.org) and follow the installation instructions for your operating system.
- **A code editor**: Such as Visual Studio Code or PyCharm, to edit your `.env` file and other script files if necessary.

## Setup Instructions

### **1. Download the Project**

Download the zip file of the project or clone it using Git:

```
git clone https://github.com/vitaliksandalik/evm-sender.git
```

### **2. Install Python Dependencies**

Open your terminal (Command Prompt or PowerShell on Windows, Terminal on Mac) and navigate to the project directory:

```
cd path/to/project-directory
```

Install the required Python packages by running:

```
pip install -r requirements.txt
```

3. **Configure the Project**

   - Find the `.env.example` file in the project folder.
   - Make a copy of this file and rename the copy to `.env`.
   - Open the `.env` file with a text editor (like Notepad).
     - You will need a **Private Key** to interact with the blockchain. **IMPORTANT: Never share your private key with anyone.**
     - Replace `YOUR_PRIVATE_KEY_HERE` in the `.env` file with your actual private key.
     - Save and close the `.env` file.
   - Open `addresses.txt`
     - Place addresses to which you want to send transactions.
     - Ensure each address is on a new line.
     - Save and close `addresses.txt`.
   - Open `config.py`
     - Select a chain from the list and write it in the `SELECTED_CHAIN` variable.
     - Select the amount to send and write it in the `AMOUNT_TO_SEND` variable.
     - If you want to send a TOKEN (not the native blockchain cryptocurrency):
       1. Copy the contract address and write it in the `TOKEN_CONTRACT_ADDRESS` variable.
     - If you want to send the native blockchain cryptocurrency, leave `TOKEN_CONTRACT_ADDRESS` as an empty string.
     - Save and close `config.py`.

4. **Understanding Project Files**

   - `main.py`: The main script you will run. It sends transactions using Web3.
   - `config.py`: Contains configuration like the blockchain network and amount to send.
   - `chains.json`: A list of supported blockchain networks and their configurations.
   - `erc20_abi.py`: The ABI for ERC-20 tokens, necessary for token transactions.
   - `utils.py`: Utility functions, including logging setup.
   - `addresses.txt`: A text file where you list the addresses to send transactions to. Make sure each address is on a new line.

5. **Running the Project**

   - Ensure you're in the project's directory in your terminal or command prompt.
   - Run the script by typing: `python main.py`.
   - The script will perform transactions as configured in `config.py` and `addresses.txt`.

## Safety and Security Tips

- **Private Keys**: Never share your private keys. Keep them secret and secure.
- **Testnet First**: Before running this on the mainnet, try everything on a testnet to ensure it works as expected without risking real funds.
- **Understand Transactions**: Be aware that transactions may involve fees (gas) that will be deducted from your wallet.

## Troubleshooting

- **Errors Running the Script**: Make sure all steps in the setup are correctly followed. Check if Python and all required libraries are installed.
- **Transaction Failures**: Insufficient funds or incorrect configuration can cause this. Verify your `.env` settings and blockchain network status.

## Support

If you encounter any issues or have questions, please check the FAQs or contact the support team (provide contact details here).

Thank you for using our Web3 project!
