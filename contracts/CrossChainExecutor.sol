/// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

// Placeholder for LayerZero or Wormhole interfaces
interface ILayerZeroEndpoint {
    function sendPayload(uint16 _dstChainId, bytes calldata _payload, address _refundAddress) external payable;
    function receivePayload(uint16 _srcChainId, bytes calldata _payload) external;
}

interface IWormhole {
    struct VM {
        uint8 version;
        uint32 timestamp;
        uint32 nonce;
        uint16 emitterChainId;
        bytes32 emitterAddress;
        uint64 sequence;
        uint8 consistencyLevel;
        bytes payload;
        uint32 guardianSetIndex;
        bytes32[] signatures;
        bytes32 hash;
    }

    function publishMessage(uint32 nonce, bytes memory payload, uint8 consistencyLevel) external payable returns (uint64 sequence);
    function parseAndVerifyVMAs(bytes memory encodedVmAs) external view returns (bytes33[] memory hashDigests, IWormhole.VM[] memory vm);
}

/**
 * @title CrossChainExecutor
 * @dev Contract to facilitate cross-chain governance actions using LayerZero or Wormhole
 */
contract CrossChainExecutor is Initializable, AccessControlUpgradeable, UUPSUpgradeable {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE");

    ILayerZeroEndpoint public layerZeroEndpoint;
    IWormhole public wormhole;

    // Circuit breaker state
    bool public crossChainPaused;
    mapping(uint16 => bool) public chainPaused; // Per-chain pause state
    
    // Emergency limits
    uint256 public dailyTransactionLimit;
    uint256 public currentDayTransactions;
    uint256 public lastResetTimestamp;

    // Mapping to store pending cross-chain transactions
    mapping(uint256 => bytes) public pendingCrossChainPayloads;
    uint256 public nextPayloadId;

    event CrossChainTxInitiated(uint256 indexed payloadId, uint16 dstChainId, bytes payload);
    event CrossChainTxReceived(uint256 indexed payloadId, uint16 srcChainId, bytes payload);
    event CrossChainPaused(address indexed pauser, bool paused);
    event ChainPaused(uint16 indexed chainId, bool paused);
    event DailyLimitUpdated(uint256 newLimit);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address _layerZeroEndpoint, address _wormhole) public initializer {
        __AccessControl_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(GOVERNANCE_ROLE, msg.sender);

        layerZeroEndpoint = ILayerZeroEndpoint(_layerZeroEndpoint);
        wormhole = IWormhole(_wormhole);
        
        // Initialize circuit breaker settings
        dailyTransactionLimit = 100; // Default limit
        lastResetTimestamp = block.timestamp;
    }

    /**
     * @dev Modifier to check if cross-chain operations are not paused
     */
    modifier whenCrossChainNotPaused() {
        require(!crossChainPaused, "Cross-chain operations paused");
        _;
    }

    /**
     * @dev Modifier to check if specific chain is not paused
     */
    modifier whenChainNotPaused(uint16 chainId) {
        require(!chainPaused[chainId], "Chain operations paused");
        _;
    }

    /**
     * @dev Modifier to check daily transaction limits
     */
    modifier withinDailyLimit() {
        _resetDailyCounterIfNeeded();
        require(currentDayTransactions < dailyTransactionLimit, "Daily transaction limit exceeded");
        currentDayTransactions++;
        _;
    }

    /**
     * @dev Emergency pause for all cross-chain operations
     */
    function pauseCrossChain() external onlyRole(GUARDIAN_ROLE) {
        crossChainPaused = true;
        emit CrossChainPaused(msg.sender, true);
    }

    /**
     * @dev Unpause cross-chain operations
     */
    function unpauseCrossChain() external onlyRole(ADMIN_ROLE) {
        crossChainPaused = false;
        emit CrossChainPaused(msg.sender, false);
    }

    /**
     * @dev Pause operations for a specific chain
     */
    function pauseChain(uint16 chainId) external onlyRole(GUARDIAN_ROLE) {
        chainPaused[chainId] = true;
        emit ChainPaused(chainId, true);
    }

    /**
     * @dev Unpause operations for a specific chain
     */
    function unpauseChain(uint16 chainId) external onlyRole(ADMIN_ROLE) {
        chainPaused[chainId] = false;
        emit ChainPaused(chainId, false);
    }

    /**
     * @dev Update daily transaction limit
     */
    function setDailyTransactionLimit(uint256 newLimit) external onlyRole(ADMIN_ROLE) {
        dailyTransactionLimit = newLimit;
        emit DailyLimitUpdated(newLimit);
    }

    /**
     * @dev Reset daily counter if 24 hours have passed
     */
    function _resetDailyCounterIfNeeded() internal {
        if (block.timestamp >= lastResetTimestamp + 1 days) {
            currentDayTransactions = 0;
            lastResetTimestamp = block.timestamp;
        }
    }

    /**
     * @dev Send a cross-chain message via LayerZero
     * @param _dstChainId The destination chain ID
     * @param _payload The payload to send
     */
    function sendLayerZeroMessage(uint16 _dstChainId, bytes memory _payload) 
        external 
        onlyRole(GOVERNANCE_ROLE) 
        whenCrossChainNotPaused 
        whenChainNotPaused(_dstChainId)
        withinDailyLimit
        payable 
    {
        layerZeroEndpoint.sendPayload(_dstChainId, _payload, payable(address(this)));
        uint256 payloadId = nextPayloadId++;
        pendingCrossChainPayloads[payloadId] = _payload;
        emit CrossChainTxInitiated(payloadId, _dstChainId, _payload);
    }

    /**
     * @dev Receive a cross-chain message via LayerZero (called by LayerZero endpoint)
     * @param _srcChainId The source chain ID
     * @param _payload The received payload
     */
    function lzReceive(uint16 _srcChainId, bytes calldata _payload) external {
        // Only the LayerZero endpoint can call this function
        require(msg.sender == address(layerZeroEndpoint), "Unauthorized: only LayerZero endpoint");
        // Process the received payload
        // Example: decode payload and execute action
        uint256 payloadId = nextPayloadId++; // This would need to be correlated with sent messages
        emit CrossChainTxReceived(payloadId, _srcChainId, _payload);
    }

    /**
     * @dev Send a cross-chain message via Wormhole
     * @param _payload The payload to send
     * @param _consistencyLevel The consistency level for Wormhole message
     */
    function sendWormholeMessage(bytes memory _payload, uint8 _consistencyLevel) 
        external 
        onlyRole(GOVERNANCE_ROLE) 
        whenCrossChainNotPaused 
        withinDailyLimit
        payable 
        returns (uint64) 
    {
        uint64 sequence = wormhole.publishMessage(0, _payload, _consistencyLevel);
        uint256 payloadId = nextPayloadId++;
        pendingCrossChainPayloads[payloadId] = _payload;
        emit CrossChainTxInitiated(payloadId, 0, _payload); // Chain ID 0 for Wormhole for now
        return sequence;
    }

    /**
     * @dev Verify and process a Wormhole VAA (Verified Action Approval)
     * @param encodedVmAs The encoded VAA to verify
     */
    function receiveWormholeMessage(bytes memory encodedVmAs) external onlyRole(GOVERNANCE_ROLE) {
        // In a real scenario, this would involve more complex VAA parsing and verification
        // For simplicity, we'll just parse and emit an event
        (bytes33[] memory hashDigests, IWormhole.VM[] memory vm) = wormhole.parseAndVerifyVMAs(encodedVmAs);
        // Further logic to process the VAA and execute actions based on its content
        uint256 payloadId = nextPayloadId++; // This would need to be correlated with sent messages
        emit CrossChainTxReceived(payloadId, 0, encodedVmAs); // Chain ID 0 for Wormhole for now
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}
}


