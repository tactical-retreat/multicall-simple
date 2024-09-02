from enum import IntEnum
from typing import Optional, List

from eth_abi import encode, decode
from eth_utils import function_signature_to_4byte_selector
from web3 import Web3
from web3._utils.abi import normalize_event_input_types
from web3.contract.contract import ContractFunction
from web3.eth import Eth

MULTICALL_AVAX_ADDRESS = Web3.to_checksum_address('0xca11bde05977b3631167028862be2a173976ca11')


class Network(IntEnum):
    Mainnet = 1
    Rinkeby = 4
    Görli = 5
    Kovan = 42
    BSC = 56
    BSCTestnet = 97
    xDai = 100

    @property
    def multicall_adddress(self) -> str:
        return {
            Network.Mainnet: '0xeefBa1e63905eF1D7ACbA5a8513c70307C1cE441',
            Network.Rinkeby: '0x42Ad527de7d4e9d9d011aC45B31D8551f8Fe9821',
            Network.Görli: '0x77dCa2C955b15e9dE4dbBCf1246B4B85b651e50e',
            Network.Kovan: '0x2cc8688C5f75E365aaEEb4ea8D6a480405A48D2A',
            Network.BSC: '0x1Ee38d535d541c55C9dae27B12edf090C608E6Fb',
            Network.BSCTestnet: '0x6e5bb1a5ad6f68a8d7d6a5e47750ec15773d6042',
            Network.xDai: '0xb5b692a88BDFc81ca69dcB1d924f59f0413A602a',
        }[self]


class FunctionInput(object):
    def __init__(
            self,
            name: str,
            value: any,
            solidity_type: str
    ):
        self.name = name
        self.value = value
        self.solidity_type = solidity_type


class FunctionResult(object):
    def __init__(
            self,
            contract_address: str,
            function_name: str,
            inputs: list[FunctionInput],
            results: list[any]
    ):
        self.contract_address = contract_address
        self.function_name = function_name
        self.inputs = inputs
        self.results = results


class AggregateResult(object):
    def __init__(
            self,
            block_number: int,
            results: list[FunctionResult]
    ):
        self.block_number = block_number
        self.results = results


class FunctionSignature:
    def __init__(
            self,
            function: ContractFunction
    ):
        self.name = function.abi['name']

        self.inputs = [{
            'name': arg['name'],
            'type': arg['type']
        } for arg in normalize_event_input_types(function.abi.get('inputs', []))]
        self.input_types = [inp['type'] for inp in self.inputs]
        input_types_signature = '({})'.format(','.join(self.input_types))
        self.output_types = [arg['type'] for arg in normalize_event_input_types(function.abi.get('outputs', []))]
        self.signature = '{}{}'.format(self.name, input_types_signature)
        self.fourbyte = function_signature_to_4byte_selector(self.signature)

    def encode_data(self, args=None) -> bytes:
        return self.fourbyte + encode(self.input_types, args)

    def decode_data(self, output: bytes):
        return decode(self.output_types, output)

class Function:
    def __init__(
            self,
            function: ContractFunction
    ):
        self.__signature = FunctionSignature(function)
        self.__function = function

    @property
    def name(self) -> str:
        return self.__function.function_identifier

    @property
    def arguments(self) -> List[any]:
        return list(self.__function.arguments)

    @property
    def inputs(self) -> List[FunctionInput]:
        return [
            FunctionInput(
                name=_input['name'],
                value=argument,
                solidity_type=_input['type']
            )

            for _input, argument in zip(
                self.__signature.inputs,
                self.__function.arguments
            )
        ]

    @property
    def address(self) -> str:
        return self.__function.address

    @property
    def data(self) -> bytes:
        return self.__signature.encode_data(self.__function.args)

    def decode_output(
            self,
            output
    ) -> list[any]:
        return self.__signature.decode_data(output)


abi = [
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "target",
                        "type": "address"
                    },
                    {
                        "internalType": "bytes",
                        "name": "callData",
                        "type": "bytes"
                    }
                ],
                "internalType": "struct Multicall.Call[]",
                "name": "calls",
                "type": "tuple[]"
            }
        ],
        "name": "aggregate",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "blockNumber",
                "type": "uint256"
            },
            {
                "internalType": "bytes[]",
                "name": "returnData",
                "type": "bytes[]"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "blockNumber",
                "type": "uint256"
            }
        ],
        "name": "getBlockHash",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "blockHash",
                "type": "bytes32"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getCurrentBlockCoinbase",
        "outputs": [
            {
                "internalType": "address",
                "name": "coinbase",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getCurrentBlockDifficulty",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "difficulty",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getCurrentBlockGasLimit",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "gaslimit",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getCurrentBlockTimestamp",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "addr",
                "type": "address"
            }
        ],
        "name": "getEthBalance",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "balance",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getLastBlockHash",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "blockHash",
                "type": "bytes32"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]


class Multicall(object):
    def __init__(
            self,
            eth: Eth,
            address: Optional[str] = None
    ):
        self.eth = eth
        self.address = address or Network(eth.chain_id).multicall_adddress
        self.abi = abi
        self.contract = self.eth.contract(address=self.address, abi=self.abi)

    def aggregate(
            self,
            calls: List[ContractFunction]
    ) -> AggregateResult:
        funcs = [Function(call) for call in calls]

        block_number, outputs = self.contract.functions.aggregate(
            [[func.address, func.data] for func in funcs]
        ).call()

        return AggregateResult(
            block_number=block_number,
            results=[
                FunctionResult(
                    contract_address=func.address,
                    function_name=func.name,
                    inputs=func.inputs,
                    results=list(func.decode_output(output))
                )
                for func, output in zip(funcs, outputs)
            ]
        )
