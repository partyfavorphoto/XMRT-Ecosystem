/// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

/**
 * @title PolicyEngine
 * @dev Defines and enforces AI agent spending limits and policies
 */
contract PolicyEngine is Initializable, AccessControlUpgradeable, UUPSUpgradeable {
    // Roles
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");

    // Policy structure
    struct Policy {
        uint256 id;
        string name;
        string description;
        bool isActive;
        bytes data; // Encoded policy data (e.g., spending limits, rules)
    }

    // Spending limits for AI agents per token
    struct SpendingLimit {
        address tokenAddress;
        uint256 dailyLimit;
        uint256 totalLimit;
        uint256 dailySpent;
        uint256 totalSpent;
        uint256 lastResetTime;
        bool isActive;
    }

    // State variables
    uint256 public policyCount;
    mapping(uint256 => Policy) public policies;
    mapping(address => mapping(address => SpendingLimit)) public aiAgentSpendingLimits; // aiAgent => tokenAddress => SpendingLimit

    // Events
    event PolicyCreated(uint256 indexed policyId, string name, bool isActive);
    event PolicyUpdated(uint256 indexed policyId, string name, bool isActive);
    event PolicyActivated(uint256 indexed policyId);
    event PolicyDeactivated(uint256 indexed policyId);
    event AISpendingLimitSet(address indexed aiAgent, address indexed tokenAddress, uint256 dailyLimit, uint256 totalLimit);
    event AISpendingRecorded(address indexed aiAgent, address indexed tokenAddress, uint256 amount);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize() public initializer {
        __AccessControl_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(GOVERNANCE_ROLE, msg.sender);
    }

    /**
     * @dev Create a new policy
     */
    function createPolicy(string memory name, string memory description, bytes memory data) external onlyRole(GOVERNANCE_ROLE) returns (uint256) {
        policyCount++;
        policies[policyCount] = Policy({
            id: policyCount,
            name: name,
            description: description,
            isActive: true,
            data: data
        });
        emit PolicyCreated(policyCount, name, true);
        return policyCount;
    }

    /**
     * @dev Update an existing policy
     */
    function updatePolicy(uint256 policyId, string memory name, string memory description, bytes memory data) external onlyRole(GOVERNANCE_ROLE) {
        require(policies[policyId].id != 0, "Policy does not exist");
        policies[policyId].name = name;
        policies[policyId].description = description;
        policies[policyId].data = data;
        emit PolicyUpdated(policyId, name, policies[policyId].isActive);
    }

    /**
     * @dev Activate a policy
     */
    function activatePolicy(uint256 policyId) external onlyRole(GOVERNANCE_ROLE) {
        require(policies[policyId].id != 0, "Policy does not exist");
        require(!policies[policyId].isActive, "Policy already active");
        policies[policyId].isActive = true;
        emit PolicyActivated(policyId);
    }

    /**
     * @dev Deactivate a policy
     */
    function deactivatePolicy(uint256 policyId) external onlyRole(GOVERNANCE_ROLE) {
        require(policies[policyId].id != 0, "Policy does not exist");
        require(policies[policyId].isActive, "Policy already inactive");
        policies[policyId].isActive = false;
        emit PolicyDeactivated(policyId);
    }

    /**
     * @dev Set spending limits for a specific AI agent and token
     */
    function setAISpendingLimit(
        address aiAgent,
        address tokenAddress,
        uint256 dailyLimit,
        uint256 totalLimit
    ) external onlyRole(GOVERNANCE_ROLE) {
        require(aiAgent != address(0), "Invalid AI agent address");
        require(tokenAddress != address(0) || dailyLimit == 0 && totalLimit == 0, "Invalid token address for non-zero limits");

        aiAgentSpendingLimits[aiAgent][tokenAddress] = SpendingLimit({
            tokenAddress: tokenAddress,
            dailyLimit: dailyLimit,
            totalLimit: totalLimit,
            dailySpent: 0,
            totalSpent: 0,
            lastResetTime: block.timestamp,
            isActive: true
        });

        emit AISpendingLimitSet(aiAgent, tokenAddress, dailyLimit, totalLimit);
    }

    /**
     * @dev Record AI agent spending and enforce limits
     * This function should be called by the DAO_Treasury before executing a transfer.
     */
    function recordAISpending(address aiAgent, address tokenAddress, uint256 amount) external onlyRole(GOVERNANCE_ROLE) returns (bool) {
        SpendingLimit storage limit = aiAgentSpendingLimits[aiAgent][tokenAddress];
        require(limit.isActive, "Spending limit not set or inactive for this agent/token");

        // Reset daily spending if a day has passed
        if (block.timestamp >= limit.lastResetTime + 1 days) {
            limit.dailySpent = 0;
            limit.lastResetTime = block.timestamp;
        }

        // Check limits
        require(limit.dailySpent + amount <= limit.dailyLimit, "Daily spending limit exceeded for AI agent");
        require(limit.totalSpent + amount <= limit.totalLimit, "Total spending limit exceeded for AI agent");

        // Update spending tracking
        limit.dailySpent += amount;
        limit.totalSpent += amount;

        emit AISpendingRecorded(aiAgent, tokenAddress, amount);
        return true;
    }

    /**
     * @dev Get spending limits for a specific AI agent and token
     */
    function getAISpendingLimit(address aiAgent, address tokenAddress) external view returns (
        uint256 dailyLimit,
        uint256 totalLimit,
        uint256 dailySpent,
        uint256 totalSpent,
        uint256 dailyRemaining,
        uint256 totalRemaining
    ) {
        SpendingLimit storage limit = aiAgentSpendingLimits[aiAgent][tokenAddress];
        
        uint256 currentDailySpent = limit.dailySpent;
        if (block.timestamp >= limit.lastResetTime + 1 days) {
            currentDailySpent = 0;
        }

        return (
            limit.dailyLimit,
            limit.totalLimit,
            currentDailySpent,
            limit.totalSpent,
            limit.dailyLimit - currentDailySpent,
            limit.totalLimit - limit.totalSpent
        );
    }

    /**
     * @dev Authorize contract upgrades
     */
    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}
}


