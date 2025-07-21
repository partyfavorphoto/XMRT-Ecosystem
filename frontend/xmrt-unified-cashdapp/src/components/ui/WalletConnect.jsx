import React from 'react';
import { useWeb3 } from '../../hooks/useWeb3';
import { Button } from './button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Badge } from './badge';
import { Wallet, ExternalLink, Copy, AlertCircle } from 'lucide-react';

export const WalletConnect = ({ className = '' }) => {
  const {
    account,
    balance,
    xmrtBalance,
    isConnected,
    isLoading,
    error,
    chainId,
    targetChainId,
    connectWallet,
    disconnectWallet,
    contractAddress,
  } = useWeb3();

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const formatBalance = (balance) => {
    const num = parseFloat(balance);
    if (num === 0) return '0';
    if (num < 0.0001) return '< 0.0001';
    return num.toFixed(4);
  };

  const isCorrectNetwork = chainId === targetChainId;

  if (!isConnected) {
    return (
      <Card className={`w-full max-w-md ${className}`}>
        <CardHeader className="text-center">
          <CardTitle className="flex items-center justify-center gap-2">
            <Wallet className="h-5 w-5" />
            Connect Wallet
          </CardTitle>
          <CardDescription>
            Connect your MetaMask wallet to interact with XMRT
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}
          
          <Button 
            onClick={connectWallet} 
            disabled={isLoading}
            className="w-full"
            size="lg"
          >
            {isLoading ? 'Connecting...' : 'Connect MetaMask'}
          </Button>
          
          <div className="text-xs text-gray-500 text-center">
            Make sure you're on Sepolia Testnet
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`w-full max-w-md ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Wallet className="h-5 w-5" />
            Wallet Connected
          </span>
          <Badge variant={isCorrectNetwork ? "default" : "destructive"}>
            {isCorrectNetwork ? 'Sepolia' : 'Wrong Network'}
          </Badge>
        </CardTitle>
        <CardDescription>
          {formatAddress(account)}
          <Button
            variant="ghost"
            size="sm"
            className="ml-2 h-auto p-1"
            onClick={() => copyToClipboard(account)}
          >
            <Copy className="h-3 w-3" />
          </Button>
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {!isCorrectNetwork && (
          <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">Please switch to Sepolia Testnet</span>
          </div>
        )}
        
        {/* Balances */}
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">ETH Balance:</span>
            <span className="text-sm">{formatBalance(balance)} ETH</span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">XMRT Balance:</span>
            <span className="text-sm">{formatBalance(xmrtBalance)} XMRT</span>
          </div>
        </div>
        
        {/* Contract Info */}
        <div className="pt-3 border-t">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Contract:</span>
            <div className="flex items-center gap-1">
              <span>{formatAddress(contractAddress)}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-1"
                onClick={() => copyToClipboard(contractAddress)}
              >
                <Copy className="h-3 w-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-1"
                onClick={() => window.open(`https://sepolia.etherscan.io/address/${contractAddress}`, '_blank')}
              >
                <ExternalLink className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={() => window.open(`https://sepolia.etherscan.io/address/${account}`, '_blank')}
          >
            View on Explorer
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={disconnectWallet}
          >
            Disconnect
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default WalletConnect;

