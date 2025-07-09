
    const HDWalletProvider = require('@truffle/hdwallet-provider');
    const fs = require('fs');
    const mnemonic = fs.readFileSync(".secret").toString().trim();
    
    module.exports = {
      networks: {
        sepolia: {
          provider: () => new HDWalletProvider(
            mnemonic,
            "https://sepolia.infura.io/v3/c843a693bc5d43d1aee471d2491f2414"
          ),
          network_id: 11155111,
          gas: 5500000,
          confirmations: 2,
          timeoutBlocks: 200,
          skipDryRun: true
        }
      },
      compilers: {
        solc: {
          version: "0.8.0",
          settings: {
            optimizer: {
              enabled: true,
              runs: 200
            }
          }
        }
      }
    };
    