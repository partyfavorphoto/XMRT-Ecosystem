// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IAgent {
    function executeProposal(bytes calldata data) external returns (bool);
}
