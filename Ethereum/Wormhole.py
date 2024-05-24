from collections import defaultdict
from SafeERC20 import SafeERC20
from BytesLib import BytesLib
from Crypto.Hash import keccak

MAX_UINT64 = (1 << 64) - 1

def keccak256(data):
    hash_object = keccak.new(digest_bits=256)
    hash_object.update(data)
    return hash_object.hexdigest()

class Contract:
    def __init__(self):
        self.wrappedAssets = defaultdict(bool)
        self.chainID = 2
        self.address = '0x3ee18B2214AFF97000D974cf647E7C347E8fa585'.lower()
        self.msg_sender = '0x5bd1b6b7ec91eb8b21e9e7349c6d4bebf0078435'.lower()
        self.msg_value = 0
        self.finality = 0

        self._state = defaultdict()
        self._state['outstandingBridged'] = defaultdict(int)
        self._state['bridgeContracts'] = defaultdict(int)

        self.ERC20_Tokens = defaultdict(SafeERC20)

        SmarDex = SafeERC20()
        SmarDex.constructor('SmarDex', 'SDEX')
        SmarDex.set_balance('0x5Bd1b6b7EC91eb8B21e9e7349c6d4BebF0078435'.lower(), 38012880422754149229822)
        SmarDex.set_balance('0x3ee18B2214AFF97000D974cf647E7C347E8fa585'.lower(), 1296037968379177100000000000)
        SmarDex.set_allowances('0x5Bd1b6b7EC91eb8B21e9e7349c6d4BebF0078435'.lower(), '0x3ee18B2214AFF97000D974cf647E7C347E8fa585'.lower(), 38012880422754149229822)
        SmarDex.set_msgSender('0x3ee18b2214aff97000d974cf647e7c347e8fa585'.lower())

        self.ERC20_Tokens['0x5DE8ab7E27f6E7A1fFf3E5B337584Aa43961BEeF'.lower()] = SmarDex
    
    # https://etherscan.io/tx/0x00718350702d0f67f0d3090bdf2f8564cfa8927f749dffcf87688b348223eeae
    def transferTokens(self, token, amount, recipientChain, recipient, arbiterFee, nonce) -> int:
        transferResult = self._transferTokens(token, amount, arbiterFee)
        sequence = self.logTransfer(transferResult['tokenChain'], transferResult['tokenAddress'], transferResult['normalizedAmount'], recipientChain, recipient, transferResult['normalizedArbiterFee'], transferResult['wormholeFee'], nonce);
        return sequence

    def _transferTokens(self, token, amount, arbiterFee) -> dict:
        tokenChain = 0
        tokenAddress = 0x0
        if self.isWrappedAsset(token):
            print('Not Wrapped Asset') #  TODO: do a mapping
        else:
            tokenChain = self.chainID
            tokenAddress = token[2:].rjust(64, '0')

        print('Querying Token\'s decimals()')
        # (,bytes memory queriedDecimals) = token.staticcall(abi.encodeWithSignature("decimals()"));
        # uint8 decimals = abi.decode(queriedDecimals, (uint8));
        decimals = self.ERC20_Tokens[token.lower()].decimals()
        amount = self.deNormalizeAmount(self.normalizeAmount(amount, decimals), decimals)

        if tokenChain == self.chainID:

            # print('Querying Balance Before')
            # (,bytes memory queriedBalanceBefore) = token.staticcall(abi.encodeWithSelector(IERC20.balanceOf.selector, address(this)));
            # uint256 balanceBefore = abi.decode(queriedBalanceBefore, (uint256));
            balanceBefore = self.ERC20_Tokens[token.lower()].balanceOf(self.address)

            # print('Transferring Tokens') # TODO
            # SafeERC20.safeTransferFrom(IERC20(token), msg.sender, address(this), amount);
            self.ERC20_Tokens[token.lower()].safeTransferFrom(token, self.msg_sender, self.address, amount)

            # print('Querying Balance After')
            # (,bytes memory queriedBalanceAfter) = token.staticcall(abi.encodeWithSelector(IERC20.balanceOf.selector, address(this)));
            # uint256 balanceAfter = abi.decode(queriedBalanceAfter, (uint256));
            balanceAfter = self.ERC20_Tokens[token.lower()].balanceOf(self.address)

            amount = balanceAfter - balanceBefore
        else:
            # print('Transfering Tokens')
            # SafeERC20.safeTransferFrom(IERC20(token), msg.sender, address(this), amount);
            self.ERC20_Tokens[token.lower()].safeTransferFrom(token, self.msg_sender, self.address, amount)

            # print('Burning Tokens')
            # TokenImplementation(token).burn(address(this), amount); # TODO: burn to address x
            self.ERC20_Tokens[token.lower()]._burn(self.address, amount)

            # tokens are wrapped and their collateral is being withdrew from the other side so these tokens are no longer backed by anything

        normalizedAmount = self.normalizeAmount(amount, decimals)
        normalizedArbiterFee = self.normalizeAmount(arbiterFee, decimals)

        if tokenChain == self.chainID:
            self.bridgeOut(token, normalizedAmount)

        transferResult = {'tokenChain': tokenChain, 'tokenAddress': tokenAddress, 'normalizedAmount': normalizedAmount, 'normalizedArbiterFee': normalizedArbiterFee, 'wormholeFee': self.msg_value}
        
        return transferResult
        

    def isWrappedAsset(self, token):
        return self.wrappedAssets[token]

    def normalizeAmount(self, amount: int, decimals: int) -> int:
        if decimals > 8:
            amount = amount // 10 ** (decimals - 8)
        
        return amount

    def deNormalizeAmount(self, amount: int, decimals: int) -> int:
        if decimals > 8:
            amount *= 10 ** (decimals - 8)
        
        return amount
    
    def bridgeIn(self, token, normalizedAmount):
        self.setOutstandingBridge(token, self.outstandingBridged(token) - normalizedAmount)

    def bridgeOut(self, token, normalizedAmount):
        outstandingAmount = self.outstandingBridged(token)
        assert outstandingAmount + normalizedAmount <= MAX_UINT64, "Transfer Exceeds Max Outstanding Bridged Token Amount"
        self.setOutstandingBridge(token, outstandingAmount + normalizedAmount)
        return None

    def outstandingBridged(self, token):
        return self._state['outstandingBridged'][token]

    def setOutstandingBridge(self, token, amount):
        self._state['outstandingBridged'][token] = amount

    def logTransfer(self, tokenChain, tokenAddress, amount, recipientChain, recipient, fee, callValue, nonce):
        transfer = {'payloadID': 1, 'amount': amount, 'tokenAddress': tokenAddress, 'tokenChain': tokenChain, 'to': recipient, 'toChain': recipientChain, 'fee': fee}

        print(f'Nonce: {nonce}')

        encodedResult = self.encodedTransfer(transfer)

        print(f'Payload: {encodedResult}')

        print(f'Consistency Level: {self.finality}')

        return None

    def encodedTransfer(self, transfer):
        payloadID = transfer['payloadID']
        string = hex(payloadID)[2:]
        encode = string.rjust(2, '0')

        amount = transfer['amount']
        string = hex(amount)[2:]
        encode += string.rjust(64, '0')

        tokenAddress = transfer['tokenAddress']
        encode += tokenAddress.rjust(64, '0')

        tokenChain = transfer['tokenChain']
        string = hex(tokenChain)[2:]
        encode += string.rjust(4, '0')

        toAddress = transfer['to']
        string = toAddress[2:]
        encode += string.rjust(64, '0')

        toChain = transfer['toChain']
        string = hex(toChain)[2:]
        encode += string.rjust(4, '0')

        fee = transfer['fee']
        string = hex(fee)[2:]
        encode += string.rjust(64, '0')

        return encode

    def completeTransfer(self, encodedVM):
        self._completeTransfer(encodedVM, False)

    def _completeTransfer(self, encodedVM, unwrapWETH):
        vm, valid, reason = self.parseAndVerifyVM(encodedVM)

        assert valid, reason
        assert self.verifyBridge(vm), "invalid emitter"

        transfer = self._parseCommonTransfer(vm['payload'])

        transferRecipient = self._truncateAddress(transfer['to'])

        if transfer['payloadID'] == 3:
            assert self.msg_sender == transferRecipient, "Invalid Sender"
        
        assert not self.isTransferCompleted(vm['hash']), "Transfer Already Completed"
        self.setTransferCompleted(vm['hash'])

        self.TransferRedeemed(vm['chainID'], vm['emitterAddress'], vm['sequence'])

        assert transfer['toChain'] == self.chainID, 'Invalid Target Chain'

        transferToken = None
        if transfer['tokenChain'] == self.chainID:
            transferToken = self._truncateAddress(transfer['tokenAddress'])

            self.bridgeIn(transferToken, transfer['amount'])
        else:
            # It is a wrapped asset, so it will need to be minted

            # address wrapped = wrappedAsset(transfer.tokenChain, transfer.tokenAddress);
            # require(wrapped != address(0), "no wrapper for this token created yet");

            # transferToken = IERC20(wrapped);
            print('Wrapped Asset')
        
        # TODO:: if querying decimals, need to make an ERC20 Token
        decimals = 18

        nativeAmount = self.deNormalizeAmount(transfer['amount'], decimals)
        nativeFee = self.deNormalizeAmount(transfer['fee'], decimals)

        if nativeFee > 0 and transferRecipient != self.msg_sender:
            
            assert nativeFee <= nativeAmount, 'Fee higher than Transferred Amount'

            if unwrapWETH:
                # transfer fee to msg.sender
                print(f'Transferring Fee to {self.msg_sender}')

                # WETH().withdraw(nativeFee);
                # payable(msg.sender).transfer(nativeFee);

            else:
                if transfer['tokenChain'] != self.chainID:
                    print('Minting Wrapped Asset')
                    # TokenImplementation(address(transferToken)).mint(msg.sender, nativeFee);

                else:
                    print(f'Transferring Native Token {transferToken}')
                    # SafeERC20.safeTransfer(transferToken, msg.sender, nativeFee);
        else:
            nativeFee = 0
        
        transferAmount = nativeAmount - nativeFee

        if unwrapWETH:
            # transfer ETH to recipient
            print(f'Transferring {transferAmount} ETH to {transferRecipient}')
            
            # WETH().withdraw(transferAmount);
            # payable(transferRecipient).transfer(transferAmount);
        
        else:
            if transfer['tokenChain'] != self.chainID:
                print('Minting Wrapped Asset')
                # TokenImplementation(address(transferToken)).mint(transferRecipient, transferAmount);
            
            else:
                print(f'Transferring Native Token {transferToken}')
                # SafeERC20.safeTransfer(transferToken, transferRecipient, transferAmount);



    def parseAndVerifyVM(self, encodedVM):
        vm = self.parseVM(encodedVM)
        (valid, reason) = self.verifyVMInternal(vm, False)

        return vm, valid, reason

    def parseVM(self, encodedVM):
        vm = {}
        index = 0

        vm['version'] = BytesLib.toUint8(encodedVM, index)
        index += 2

        vm['guardianSetIndex'] = BytesLib.toUint32(encodedVM, index)
        index += 8

        signersLen = BytesLib.toUint8(encodedVM, index)
        index += 2

        signatures = []
        for i in range(signersLen):
            guardianIndex = BytesLib.toUint8(encodedVM, index)
            index += 2

            r = BytesLib.toBytes32(encodedVM, index)
            index += 64
            s = BytesLib.toBytes32(encodedVM, index)
            index += 64
            v = BytesLib.toUint8(encodedVM, index) + 27
            index += 2

            signatures.append(guardianIndex, r, s, v)
        
        # body = BytesLib.slice(encodedVM, index, len(encodedVM) - index)
        # vm['hash'] = keccak256(keccak256(bytes.fromhex(body)))

        vm['timestamp'] = BytesLib.toUint32(encodedVM, index)
        index += 8

        vm['nonce'] = BytesLib.toUint32(encodedVM, index)
        index += 8

        vm['emitterID'] = BytesLib.toUint16(encodedVM, index)
        index += 4

        vm['emitterAddress'] = BytesLib.toBytes32(encodedVM, index)
        index += 32

        vm['sequence'] = BytesLib.toUint64(encodedVM, index)
        index += 16

        vm['consistencyLevel'] = BytesLib.toUint8(encodedVM, index)
        index += 2

        vm['payload'] = encodedVM[index:]

        return vm

    def verifyVMInternal(self, vm, checkHash):
        return True, ""
    
    def verifyBridgeVM(self, vm) -> bool:
        return self._state['bridgeContracts'][vm['emitterChainID']] == vm['emitterAddress']
    
    # TODO
    def _parseCommonTransfer(self, encoded):
        return None
    
    # TODO
    def _truncateAddress(self, address):
        return None
    
    # TODO
    def isTransferCompleted(self, hash):
        return False
    
    # TODO
    def setTransferCompleted(self, hash):
        return None
    
    # TODO
    def TransferRedeemed(self, chainID, emitterAddress, sequence):
        return None
    
    # TODO
    def wrappedAsset(tokenChain, tokenAddress):
        return None