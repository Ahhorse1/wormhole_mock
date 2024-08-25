import HECO

# https://hecoscan.io/#/transaction/0x656d3849a3c41e1d53a63f9d50a208cfe299d24fea47c6eaea6f587c3fcd107a
actual_taskHash = '219295438b17c92dbc62ee9b1874dc1a25cf55368e13d34d65325217d4acbafe'
to = '0x75e42d184b2f4b1fea2673a9f3116d1f66c90b44'
value = 100000000000000000
proof = 'heco_1e5d4be9514f61006c449518e851a8ad898e69250deb428a6d9dfa73e682d323_1'
print("Transaction: 0x656d3849a3c41e1d53a63f9d50a208cfe299d24fea47c6eaea6f587c3fcd107a")
print(HECO.check_hash(to, value, proof, actual_taskHash))
print(HECO.generate_hash(to, value, proof))

# https://hecoscan.io/#/transaction/0x53040f7932306b752abaa6cc61354f4bd6be189a58fb1b35fab9b0667aa72d68
actual_taskHash = '63333d9ba80d323ed3a2c486809215e8f1fb8c645691606b862787fad572c1c7'
to = '0x75e42d184b2f4b1fea2673a9f3116d1f66c90b44'
value = 100000000000000000
proof = 'eth_6b175474e89094c44da98b954eedeac495271d0f_d0a6c7f55dbb9f548950ce10dc05f6b10031033f557292268a473aa7a3a10dae_2'
print("\nTransactions: 0x53040f7932306b752abaa6cc61354f4bd6be189a58fb1b35fab9b0667aa72d68")
print(HECO.check_hash(to, value, proof, actual_taskHash))
print(HECO.generate_hash(to, value, proof))

# https://hecoscan.io/#/transaction/0x656d3849a3c41e1d53a63f9d50a208cfe299d24fea47c6eaea6f587c3fcd107a
actual_taskHash = '219295438b17c92dbc62ee9b1874dc1a25cf55368e13d34d65325217d4acbafe'
to = '0x75e42d184b2f4b1fea2673a9f3116d1f66c90b44'
value = 100000000000000000
proof = 'heco_1e5d4be9514f61006c449518e851a8ad898e69250deb428a6d9dfa73e682d323_1'
print("\nTransactions: 0x53040f7932306b752abaa6cc61354f4bd6be189a58fb1b35fab9b0667aa72d68")
print(HECO.check_hash(to, value, proof, actual_taskHash))
print(HECO.generate_hash(to, value, proof))

# https://etherscan.io/tx/0xbb6fe88427c2f3bc179075109d47a805dcfedab0e475eaca0d979311873e131b
actual_taskHash = 'd439f9315608aab1dd82ad6e948fe138ede7b6a180f8d9286cac4694e9206f58'
to = '0xFc146D1CaF6Ba1d1cE6dcB5b35dcBF895f50B0C4'
value = 10145000000000000000000
proof = 'heco_ad17c69cfe45e114d929ef0cf8c5d5239055da144d8e483918736ddf428bb0dc25a93448706b87aa6baa8b59c0a33d03497079b11_1'
print("\nExploited Transactions")
print(HECO.check_hash(to, value, proof, actual_taskHash))
print(HECO.generate_hash(to, value, proof))

# https://etherscan.io/tx/0x862586eda8b6f7dd68aadcac413f3f8eddb3545630baed35afa33e138576dd62
actual_taskHash = '79a98e66cf1a4332ba02690ac403f73d6b2044d3f4657b418694094dd0ac127b'
to = '0xFc146D1CaF6Ba1d1cE6dcB5b35dcBF895f50B0C4'
value = 346994000000000000000000
proof = 'heco_0ce361527b3a1e3ad571025f8b9d93330185a6d5181bfa2a78cb4557ea79af60185e4af0bc8d5f574257a1b2cf711ba81cd006040_1'
print("\nExploited Transactions")
print(HECO.check_hash(to, value, proof, actual_taskHash))
print(HECO.generate_hash(to, value, proof))