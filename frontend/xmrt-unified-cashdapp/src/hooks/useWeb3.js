import { useState, useEffect, useCallback } from 'react';
import { ethers } from 'ethers';

// XMRT Contract ABI (ERC20 standard with additional functions)
const XMRT_ABI = [
  // ERC20 Standard Functions
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address owner) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "function transferFrom(address from, address to, uint256 amount) returns (bool)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
  
  // Events
  "event Transfer(address indexed from, address indexed to, uint256 value)",
  "event Approval(address indexed owner, address indexed spender, uint256 value)",
  
  // Additional XMRT Functions (if available)
  "function mint(address to, uint256 amount) returns (bool)",
  "function burn(uint256 amount) returns (bool)",
  "function pause() returns (bool)",
  "function unpause() returns (bool)",
  "function paused() view returns (bool)",
  
  // Mining/Staking Functions (if available)
  "function stake(uint256 amount) returns (bool)",
  "function unstake(uint256 amount) returns (bool)",
  "function getStakedAmount(address account) view returns (uint256)",
  "function getRewards(address account) view returns (uint256)",
  "function claimRewards() returns (bool)",
  
  // DAO Functions (if available)
  "function vote(uint256 proposalId, bool support) returns (bool)",
  "function createProposal(string memory description) returns (uint256)",
  "function getProposal(uint256 proposalId) view returns (tuple(string description, uint256 votes, bool executed))"
];

const XMRT_CONTRACT_ADDRESS = import.meta.env.VITE_XMRT_CONTRACT_ADDRESS || '0x77307DFbc436224d5e6f2048d2b6bDfA66998a15';
const RPC_URL = import.meta.env.VITE_RPC_URL || 'https://eth-sepolia.g.alchemy.com/v2/HPua2YZ0vA5Yj8XTJH1j8HNVYvMWbifr';
const CHAIN_ID = parseInt(import.meta.env.VITE_CHAIN_ID || '11155111');

export const useWeb3 = () => {
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [contract, setContract] = useState(null);
  const [account, setAccount] = useState(null);
  const [balance, setBalance] = useState('0');
  const [xmrtBalance, setXmrtBalance] = useState('0');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chainId, setChainId] = useState(null); // eslint-disable-line no-unused-vars

  // Initialize provider
  const initializeProvider = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Try to connect to MetaMask first
      if (window.ethereum) {
        const web3Provider = new ethers.BrowserProvider(window.ethereum);
        setProvider(web3Provider);
        
        // Get network info
        const network = await web3Provider.getNetwork();
        setChainId(Number(network.chainId));
        
        return web3Provider;
      } else {
        // Fallback to RPC provider
        const rpcProvider = new ethers.JsonRpcProvider(RPC_URL);
        setProvider(rpcProvider);
        setChainId(CHAIN_ID);
        return rpcProvider;
      }
    } catch (err) {
      console.error('Failed to initialize provider:', err);
      setError('Failed to connect to blockchain network');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Connect wallet
  const connectWallet = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      if (!window.ethereum) {
        throw new Error('MetaMask not found. Please install MetaMask.');
      }

      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      });

      if (accounts.length === 0) {
        throw new Error('No accounts found');
      }

      const web3Provider = new ethers.BrowserProvider(window.ethereum);
      const web3Signer = await web3Provider.getSigner();
      const userAccount = await web3Signer.getAddress();

      // Check if we're on the correct network
      const network = await web3Provider.getNetwork();
      const currentChainId = Number(network.chainId);

      if (currentChainId !== CHAIN_ID) {
        // Try to switch to Sepolia
        try {
          await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: `0x${CHAIN_ID.toString(16)}` }],
          });
        } catch (switchError) {
          // If the chain hasn't been added to MetaMask, add it
          if (switchError.code === 4902) {
            await window.ethereum.request({
              method: 'wallet_addEthereumChain',
              params: [
                {
                  chainId: `0x${CHAIN_ID.toString(16)}`,
                  chainName: 'Sepolia Testnet',
                  nativeCurrency: {
                    name: 'Sepolia ETH',
                    symbol: 'SEP',
                    decimals: 18,
                  },
                  rpcUrls: [RPC_URL],
                  blockExplorerUrls: ['https://sepolia.etherscan.io/'],
                },
              ],
            });
          } else {
            throw switchError;
          }
        }
      }

      setProvider(web3Provider);
      setSigner(web3Signer);
      setAccount(userAccount);
      setChainId(currentChainId);
      setIsConnected(true);

      // Initialize contract
      const xmrtContract = new ethers.Contract(XMRT_CONTRACT_ADDRESS, XMRT_ABI, web3Signer);
      setContract(xmrtContract);

      return { provider: web3Provider, signer: web3Signer, account: userAccount };
    } catch (err) {
      console.error('Failed to connect wallet:', err);
      setError(err.message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Disconnect wallet
  const disconnectWallet = useCallback(() => {
    setProvider(null);
    setSigner(null);
    setContract(null);
    setAccount(null);
    setBalance('0');
    setXmrtBalance('0');
    setIsConnected(false);
    setError(null);
  }, []);

  // Get balances
  const updateBalances = useCallback(async () => {
    if (!provider || !account) return;

    try {
      // Get ETH balance
      const ethBalance = await provider.getBalance(account);
      setBalance(ethers.formatEther(ethBalance));

      // Get XMRT balance
      if (contract) {
        try {
          const xmrtBal = await contract.balanceOf(account);
          const decimals = await contract.decimals();
          setXmrtBalance(ethers.formatUnits(xmrtBal, decimals));
        } catch (contractError) {
          console.warn('Failed to get XMRT balance:', contractError);
          setXmrtBalance('0');
        }
      }
    } catch (err) {
      console.error('Failed to update balances:', err);
    }
  }, [provider, account, contract]);

  // Transfer XMRT tokens
  const transferXMRT = useCallback(async (to, amount) => {
    if (!contract || !signer) {
      throw new Error('Contract not initialized or wallet not connected');
    }

    try {
      setIsLoading(true);
      const decimals = await contract.decimals();
      const amountWei = ethers.parseUnits(amount.toString(), decimals);
      
      const tx = await contract.transfer(to, amountWei);
      await tx.wait();
      
      // Update balances after transfer
      await updateBalances();
      
      return tx;
    } catch (err) {
      console.error('Transfer failed:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [contract, signer, updateBalances]);

  // Get contract info
  const getContractInfo = useCallback(async () => {
    if (!contract) return null;

    try {
      const [name, symbol, decimals, totalSupply] = await Promise.all([
        contract.name(),
        contract.symbol(),
        contract.decimals(),
        contract.totalSupply(),
      ]);

      return {
        name,
        symbol,
        decimals: Number(decimals),
        totalSupply: ethers.formatUnits(totalSupply, decimals),
        address: XMRT_CONTRACT_ADDRESS,
      };
    } catch (err) {
      console.error('Failed to get contract info:', err);
      return null;
    }
  }, [contract]);

  // Listen for account changes
  useEffect(() => {
    if (window.ethereum) {
      const handleAccountsChanged = (accounts) => {
        if (accounts.length === 0) {
          disconnectWallet();
        } else if (accounts[0] !== account) {
          connectWallet();
        }
      };

      const handleChainChanged = (chainId) => {
        window.location.reload();
      };

      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', handleChainChanged);

      return () => {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
        window.ethereum.removeListener('chainChanged', handleChainChanged);
      };
    }
  }, [account, connectWallet, disconnectWallet]);

  // Initialize on mount
  useEffect(() => {
    initializeProvider();
  }, [initializeProvider]);

  // Update balances when connected
  useEffect(() => {
    if (isConnected && account) {
      updateBalances();
      // Set up interval to update balances every 30 seconds
      const interval = setInterval(updateBalances, 30000);
      return () => clearInterval(interval);
    }
  }, [isConnected, account, updateBalances]);

  return {
    // State
    provider,
    signer,
    contract,
    account,
    balance,
    xmrtBalance,
    isConnected,
    isLoading,
    error,
    chainId,
    
    // Actions
    connectWallet,
    disconnectWallet,
    transferXMRT,
    updateBalances,
    getContractInfo,
    
    // Constants
    contractAddress: XMRT_CONTRACT_ADDRESS,
    targetChainId: CHAIN_ID,
  };
};

