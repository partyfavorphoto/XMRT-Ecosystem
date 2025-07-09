
    // SPDX-License-Identifier: MIT
    pragma solidity ^0.8.0;
    
    import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
    
    contract Vault is ReentrancyGuard {
        address public TREASURY;
        
        constructor(address treasury) {
            TREASURY = treasury;
        }
        
        function withdraw(uint amount) public nonReentrant {
            require(msg.sender == TREASURY, "Unauthorized");
            payable(TREASURY).transfer(amount);
        }
    }
    