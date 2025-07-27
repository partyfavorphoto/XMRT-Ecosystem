// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "./DAO_Governance.sol";
import "./DAO_Treasury.sol";
import "./PolicyEngine.sol";

/**
 * @title AI_Agent_Interface
 * @dev Dedicated interface for AI agents to interact with the DAO
 */
contract AI_Agent_Interface is
    Initializable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    // Roles
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AI_AGENT_ROLE = keccak256("AI_AGENT_ROLE");
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");

    // Contract references
    DAO_Governance public daoGovernance;
    DAO_Treasury public daoTreasury;
    PolicyEngine public policyEngine;

    // AI agent action types
    enum ActionType {
        CreateProposal,
        ExecuteSpending,
        UpdateParameters,
        EmergencyAction,
        DataAnalysis,
        CommunityEngagement
    }

    // Action tracking
    struct AIAction {
        uint256 id;
        address agent;
        ActionType actionType;
        bytes data;
        uint256 timestamp;
        bool executed;
        string result;
    }

    // State variables
    mapping(uint256 => AIAction) public aiActions;
    uint256 public actionCount;
    mapping(address => uint256) public agentActionCount;
    mapping(address => uint256) public agentLastActionTime;

    // Events
    event AIActionInitiated(
        uint256 indexed actionId,
        address indexed agent,
        ActionType actionType,
        bytes data
    );
    event AIActionCompleted(
        uint256 indexed actionId,
        address indexed agent,
        bool success,
        string result
    );
    event AIProposalCreated(
        uint256 indexed actionId,
        uint256 indexed proposalId,
        address indexed agent
    );
    event AISpendingExecuted(
        uint256 indexed actionId,
        address indexed agent,
        address tokenAddress,
        uint256 amount,
        address recipient
    );

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(
        address _daoGovernance,
        address _daoTreasury,
        address _policyEngine
    ) public initializer {
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(ORACLE_ROLE, msg.sender);

        daoGovernance = DAO_Governance(_daoGovernance);
        daoTreasury = DAO_Treasury(_daoTreasury);
        policyEngine = PolicyEngine(_policyEngine);
    }

    /**
     * @dev AI agent creates a governance proposal
     */
    function createAIProposal(
        address target,
        uint256 value,
        bytes memory callData,
        string memory description,
        uint256 customThreshold
    ) external onlyRole(AI_AGENT_ROLE) whenNotPaused returns (uint256) {
        uint256 actionId = _recordAction(ActionType.CreateProposal, abi.encode(target, value, callData, description, customThreshold));

        try daoGovernance.submitAITriggeredProposal(target, value, callData, description, customThreshold) returns (uint256 proposalId) {
            _completeAction(actionId, true, string(abi.encodePacked("Proposal created with ID: ", proposalId)));
            emit AIProposalCreated(actionId, proposalId, msg.sender);
            return proposalId;
        } catch Error(string memory reason) {
            _completeAction(actionId, false, reason);
            revert(reason);
        }
    }

    /**
     * @dev AI agent executes spending from treasury
     */
    function executeAISpending(
        address tokenAddress,
        uint256 amount,
        address recipient,
        string memory purpose
    ) external onlyRole(AI_AGENT_ROLE) whenNotPaused returns (uint256) {
        uint256 actionId = _recordAction(ActionType.ExecuteSpending, abi.encode(tokenAddress, amount, recipient, purpose));

        try daoTreasury.executeAISpending(tokenAddress, amount, recipient, purpose) {
            _completeAction(actionId, true, "Spending executed successfully");
            emit AISpendingExecuted(actionId, msg.sender, tokenAddress, amount, recipient);
            return actionId;
        } catch Error(string memory reason) {
            _completeAction(actionId, false, reason);
            revert(reason);
        }
    }

    /**
     * @dev AI agent performs data analysis action
     */
    function performDataAnalysis(
        string memory analysisType,
        bytes memory parameters,
        string memory results
    ) external onlyRole(AI_AGENT_ROLE) whenNotPaused returns (uint256) {
        uint256 actionId = _recordAction(ActionType.DataAnalysis, abi.encode(analysisType, parameters));
        _completeAction(actionId, true, results);
        return actionId;
    }

    /**
     * @dev AI agent performs community engagement action
     */
    function performCommunityEngagement(
        string memory engagementType,
        bytes memory data,
        string memory outcome
    ) external onlyRole(AI_AGENT_ROLE) whenNotPaused returns (uint256) {
        uint256 actionId = _recordAction(ActionType.CommunityEngagement, abi.encode(engagementType, data));
        _completeAction(actionId, true, outcome);
        return actionId;
    }

    /**
     * @dev Get AI agent statistics
     */
    function getAgentStatistics(address agent) external view returns (
        uint256 totalActions,
        uint256 lastActionTime,
        uint256 successfulActions,
        uint256 failedActions
    ) {
        totalActions = agentActionCount[agent];
        lastActionTime = agentLastActionTime[agent];
        
        // Count successful and failed actions
        uint256 successful = 0;
        uint256 failed = 0;
        
        for (uint256 i = 0; i < actionCount; i++) {
            if (aiActions[i].agent == agent && aiActions[i].executed) {
                if (bytes(aiActions[i].result).length > 0 && 
                    keccak256(bytes(aiActions[i].result)) != keccak256(bytes("failed"))) {
                    successful++;
                } else {
                    failed++;
                }
            }
        }
        
        return (totalActions, lastActionTime, successful, failed);
    }

    /**
     * @dev Get action details
     */
    function getAction(uint256 actionId) external view returns (
        uint256 id,
        address agent,
        ActionType actionType,
        bytes memory data,
        uint256 timestamp,
        bool executed,
        string memory result
    ) {
        AIAction storage action = aiActions[actionId];
        return (
            action.id,
            action.agent,
            action.actionType,
            action.data,
            action.timestamp,
            action.executed,
            action.result
        );
    }

    /**
     * @dev Get treasury balance for AI agent
     */
    function getTreasuryBalance(address tokenAddress) external view returns (uint256) {
        return daoTreasury.getAvailableBalance(tokenAddress);
    }

    /**
     * @dev Get AI spending limits
     */
    function getSpendingLimits(address tokenAddress) external view returns (
        uint256 dailyLimit,
        uint256 totalLimit,
        uint256 dailySpent,
        uint256 totalSpent,
        uint256 dailyRemaining,
        uint256 totalRemaining
    ) {
        return policyEngine.getAISpendingLimit(msg.sender, tokenAddress);
    }

    /**
     * @dev Check if AI agent can perform action
     */
    function canPerformAction(address agent, ActionType actionType) external view returns (bool) {
        // Check if agent has the required role
        if (!hasRole(AI_AGENT_ROLE, agent)) {
            return false;
        }

        // Check if contract is paused
        if (paused()) {
            return false;
        }

        // Additional checks based on action type
        if (actionType == ActionType.EmergencyAction) {
            // Emergency actions might have additional restrictions
            return hasRole(ORACLE_ROLE, agent);
        }

        return true;
    }

    /**
     * @dev Record an AI action
     */
    function _recordAction(ActionType actionType, bytes memory data) internal returns (uint256) {
        uint256 actionId = actionCount++;
        
        aiActions[actionId] = AIAction({
            id: actionId,
            agent: msg.sender,
            actionType: actionType,
            data: data,
            timestamp: block.timestamp,
            executed: false,
            result: ""
        });

        agentActionCount[msg.sender]++;
        agentLastActionTime[msg.sender] = block.timestamp;

        emit AIActionInitiated(actionId, msg.sender, actionType, data);
        return actionId;
    }

    /**
     * @dev Complete an AI action
     */
    function _completeAction(uint256 actionId, bool success, string memory result) internal {
        aiActions[actionId].executed = true;
        aiActions[actionId].result = result;

        emit AIActionCompleted(actionId, aiActions[actionId].agent, success, result);
    }

    /**
     * @dev Set contract references
     */
    function setDAOGovernance(address _daoGovernance) external onlyRole(ADMIN_ROLE) {
        require(_daoGovernance != address(0), "Invalid address");
        daoGovernance = DAO_Governance(_daoGovernance);
    }

    function setDAOTreasury(address _daoTreasury) external onlyRole(ADMIN_ROLE) {
        require(_daoTreasury != address(0), "Invalid address");
        daoTreasury = DAO_Treasury(_daoTreasury);
    }

    function setPolicyEngine(address _policyEngine) external onlyRole(ADMIN_ROLE) {
        require(_policyEngine != address(0), "Invalid address");
        policyEngine = PolicyEngine(_policyEngine);
    }

    /**
     * @dev Pause contract
     */
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }

    /**
     * @dev Unpause contract
     */
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @dev Authorize contract upgrades
     */
    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}
}

