from Wormhole import Contract

token = '0x5DE8ab7E27f6E7A1fFf3E5B337584Aa43961BEEF'
amount = 1000000000000000000000
recipientChain = 4
recipient = '0x0000000000000000000000005bd1b6b7ec91eb8b21e9e7349c6d4bebf0078435'
arbiterFee = 0
nonce = 20
TokenBridge = Contract()
TokenBridge.transferTokens(token, amount, recipientChain, recipient, arbiterFee, nonce)